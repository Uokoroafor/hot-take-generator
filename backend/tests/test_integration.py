import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from tests.utils import MockAgent, TestDataFactory, assert_response_format


class TestEndToEndIntegration:
    """Test the complete flow from API request to response"""

    @patch("app.services.hot_take_service.OpenAIAgent")
    @patch("app.services.hot_take_service.AnthropicAgent")
    def test_complete_hot_take_generation_flow(self, mock_anthropic, mock_openai):
        # Setup mocks
        mock_openai_instance = MockAgent("OpenAI Agent", ["Controversial AI opinion!"])
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = MockAgent(
            "Claude Agent", ["Thoughtful AI perspective!"]
        )
        mock_anthropic.return_value = mock_anthropic_instance

        # Create async mock versions
        mock_openai_instance.generate_hot_take = AsyncMock(
            return_value="Controversial AI opinion!"
        )
        mock_anthropic_instance.generate_hot_take = AsyncMock(
            return_value="Thoughtful AI perspective!"
        )

        client = TestClient(app)

        # Test request
        request_data = TestDataFactory.hot_take_request(
            topic="artificial intelligence", style="controversial"
        )

        response = client.post("/api/generate", json=request_data)

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert_response_format(response_data)
        assert response_data["topic"] == "artificial intelligence"
        assert response_data["style"] == "controversial"

    def test_api_error_handling(self):
        client = TestClient(app)

        # Test missing topic
        response = client.post("/api/generate", json={"style": "controversial"})
        assert response.status_code == 422

        # Test invalid JSON
        response = client.post("/api/generate", data="invalid json")
        assert response.status_code == 422

    def test_cors_integration(self):
        client = TestClient(app)

        # Test CORS headers are present
        response = client.get("/api/styles")
        assert response.status_code == 200

        # CORS headers should be handled by the middleware
        # In a real test, you'd check for specific CORS headers


class TestAPIConsistency:
    """Test that all API endpoints return consistent data formats"""

    def test_agents_endpoint_format(self):
        client = TestClient(app)
        response = client.get("/api/agents")

        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) > 0

    def test_styles_endpoint_format(self):
        client = TestClient(app)
        response = client.get("/api/styles")

        assert response.status_code == 200
        data = response.json()
        assert "styles" in data
        assert isinstance(data["styles"], list)
        assert len(data["styles"]) > 0

    @patch("app.services.hot_take_service.HotTakeService.generate_hot_take")
    def test_generate_endpoint_consistency(self, mock_generate):
        from app.models.schemas import HotTakeResponse

        mock_response = HotTakeResponse(
            hot_take="Consistent hot take",
            topic="consistency",
            style="analytical",
            agent_used="Test Agent",
        )
        mock_generate.return_value = mock_response

        client = TestClient(app)

        # Test multiple requests return consistent format
        for style in ["controversial", "sarcastic", "optimistic"]:
            request_data = {"topic": "test", "style": style}
            response = client.post("/api/generate", json=request_data)

            assert response.status_code == 200
            assert_response_format(response.json())


class TestServiceIntegration:
    """Test integration between services and components"""

    @patch("app.agents.openai_agent.AsyncOpenAI")
    @patch("app.agents.anthropic_agent.AsyncAnthropic")
    @pytest.mark.asyncio
    async def test_agent_service_integration(
        self, mock_anthropic_client, mock_openai_client
    ):
        from app.services.hot_take_service import HotTakeService

        # Setup API client mocks
        mock_openai_instance = AsyncMock()
        mock_openai_response = AsyncMock()
        mock_openai_response.choices = [AsyncMock()]
        mock_openai_response.choices[0].message.content = "OpenAI integration test"
        mock_openai_instance.chat.completions.create.return_value = mock_openai_response
        mock_openai_client.return_value = mock_openai_instance

        mock_anthropic_instance = AsyncMock()
        mock_anthropic_response = AsyncMock()
        mock_anthropic_response.content = [AsyncMock()]
        mock_anthropic_response.content[0].text = "Anthropic integration test"
        mock_anthropic_instance.messages.create.return_value = mock_anthropic_response
        mock_anthropic_client.return_value = mock_anthropic_instance

        # Test service
        service = HotTakeService()

        # Test OpenAI agent
        result = await service.generate_hot_take("test", "controversial", "openai")
        assert result.hot_take == "OpenAI integration test"
        assert result.agent_used == "OpenAI Agent"

        # Test Anthropic agent
        result = await service.generate_hot_take("test", "philosophical", "anthropic")
        assert result.hot_take == "Anthropic integration test"
        assert result.agent_used == "Claude Agent"


class TestErrorHandling:
    """Test error handling across the application"""

    @patch("app.services.hot_take_service.HotTakeService.generate_hot_take")
    def test_service_error_propagation(self, mock_generate):
        mock_generate.side_effect = Exception("Service failure")

        client = TestClient(app)
        request_data = {"topic": "test", "style": "controversial"}

        response = client.post("/api/generate", json=request_data)
        assert response.status_code == 500
        assert "Service failure" in response.json()["detail"]

    def test_validation_errors(self):
        client = TestClient(app)

        # Test various invalid inputs
        invalid_requests = [
            {},  # Missing topic
            {"topic": ""},  # Empty topic
            {"topic": None},  # Null topic
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/generate", json=invalid_request)
            assert response.status_code == 422


class TestPerformance:
    """Basic performance and load testing"""

    @patch("app.services.hot_take_service.HotTakeService.generate_hot_take")
    def test_multiple_concurrent_requests(self, mock_generate):
        from app.models.schemas import HotTakeResponse
        import threading
        import time

        mock_generate.return_value = HotTakeResponse(
            hot_take="Performance test",
            topic="performance",
            style="controversial",
            agent_used="Test Agent",
        )

        client = TestClient(app)
        results = []
        errors = []

        def make_request():
            try:
                start_time = time.time()
                response = client.post("/api/generate", json={"topic": "test"})
                end_time = time.time()
                results.append(
                    {
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                    }
                )
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Assertions
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(result["status_code"] == 200 for result in results)

        # Check that all requests completed reasonably quickly
        avg_response_time = sum(result["response_time"] for result in results) / len(
            results
        )
        assert avg_response_time < 1.0, (
            f"Average response time too slow: {avg_response_time}s"
        )
