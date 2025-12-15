import pytest
from unittest.mock import patch, MagicMock
import os
import json
import numpy as np
from agents.coordinator_agent import process_task_from_api
from tools.pdf_reader import PDFReaderTool
import google.generativeai as genai

# Mock environment variables for the test
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "mock_gemini_api_key",
        "LLM_MODEL": "gemini-pro"
    }):
        yield

@pytest.fixture
def mock_pdf_reader_tool():
    with patch('tools.pdf_reader.PDFReaderTool', autospec=True) as MockPDFReaderTool:
        instance = MockPDFReaderTool.return_value
        instance.read_pdf_content.return_value = "This is a mock PDF content. It has multiple sentences."
        instance.chunk_text.return_value = ["Mock chunk 1.", "Mock chunk 2."]
        yield instance

@pytest.fixture
def mock_sentence_transformer():
    with patch('sentence_transformers.SentenceTransformer', autospec=True) as MockSentenceTransformer:
        instance = MockSentenceTransformer.return_value
        instance.get_sentence_embedding_dimension.return_value = 384
        instance.encode.return_value = np.random.rand(1, 384)
        yield instance

@pytest.fixture
def mock_faiss():
    with patch('faiss.read_index') as mock_read_index, \
         patch('faiss.write_index') as mock_write_index, \
         patch('faiss.IndexFlatL2') as mock_index_flat_l2:
        
        mock_index = MagicMock()
        mock_index.search.return_value = (np.array([[0.1, 0.2]]), np.array([[0, 1]]))
        mock_index_flat_l2.return_value = mock_index
        mock_read_index.return_value = mock_index
        
        yield {
            'read_index': mock_read_index,
            'write_index': mock_write_index,
            'IndexFlatL2': mock_index_flat_l2,
            'index': mock_index
        }

@pytest.fixture
def mock_open():
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = """
tasks_sequence:
  - agent: ExtractionAgent
    command: parse_and_chunk_pdf
  - agent: MemoryAgent
    command: search_knowledge_base
  - agent: AnalysisAgent
    command: generate_answer_from_context
  - agent: DeliveryAgent
    command: format_final_report
"""
        mock_open.return_value = mock_file
        yield mock_open

@pytest.fixture
def mock_gemini_model():
    with patch('google.generativeai.GenerativeModel', autospec=True) as MockGenerativeModel:
        instance = MockGenerativeModel.return_value
        mock_response = MagicMock()
        mock_response.text = "This is the mock LLM generated answer."
        instance.generate_content.return_value = mock_response
        yield instance

def test_full_workflow_success(mock_pdf_reader_tool, mock_sentence_transformer, mock_faiss, mock_open, mock_gemini_model):
    """
    Testa o fluxo completo de processamento de uma tarefa através dos agentes.
    """
    mock_payload = {
        "task_id": "T-TEST-001",
        "user_request": "Summarize the key points of the document.",
        "file_path": "data/input_pdfs/test_document.pdf",
        "workflow_hint": "default_pdf_analysis"
    }

    # Execute the main processing function
    result = process_task_from_api(mock_payload)

    # Assertions
    assert result["status"] == "success"
    assert "result" in result
    
    # Verify DeliveryAgent output structure
    assert isinstance(result["result"], dict)
    assert result["result"]["task_id"] == "T-TEST-001"
    assert result["result"]["user_query"] == "Summarize the key points of the document."
    assert result["result"]["status"] == "COMPLETED"
    assert result["result"]["report_content"] == "This is the mock LLM generated answer."

    # Verify agent interactions
    mock_pdf_reader_tool.read_pdf_content.assert_called_once_with(mock_payload["file_path"], mock_payload["task_id"])
    mock_pdf_reader_tool.chunk_text.assert_called_once()
    
    mock_sentence_transformer.encode.assert_called()
    mock_faiss['index'].add.assert_called()
    mock_faiss['index'].search.assert_called()
    
    mock_gemini_model.generate_content.assert_called_once()
    
    # Check the prompt passed to the LLM (basic check)
    args, kwargs = mock_gemini_model.generate_content.call_args
    prompt = args[0]
    assert "Mock chunk 1." in prompt
    assert mock_payload["user_request"] in prompt
    assert "Conteúdo do Documento Atual" in prompt
    assert "Conhecimento Relevante da Base de Dados" in prompt
