import os
import sys
import json
import time
import asyncio

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config.settings import settings
from backend.app.config.database import db_manager
from backend.app.services.document_service import document_service
from backend.app.rag.rag_pipeline import rag_pipeline
from backend.app.rag.vector_store import vector_store
from backend.app.utils.logger import logger

async def run_evaluation():
    print("=" * 60)
    print("  COLLEGE RAG PIPELINE EVALUATION BENCHMARK  ")
    print("=" * 60)

    # 1. Connect DB and seed sample documents
    await db_manager.connect()
    
    sample_docs = [
        ("College_Handbook_2026.txt", "Greenwood Institute of Technology — Official Student Handbook 2026", "General FAQ"),
        ("Academic_Examination_Regulations_2026.txt", "Academic Examination Regulations & Evaluation Guidelines", "Exams")
    ]
    
    for filename, title, category in sample_docs:
        filepath = os.path.join("./data/sample_documents", filename)
        if os.path.exists(filepath):
            docs = await document_service.list_documents()
            existing_doc = next((d for d in docs if d.get("fileName") == filename), None)
            if existing_doc:
                print(f"[Setup] Reprocessing {filename} with enhanced embeddings...")
                await document_service.reprocess_document(existing_doc["id"])
                await asyncio.sleep(0.8)
            else:
                print(f"[Setup] Ingesting {filename} into vector store...")
                with open(filepath, "rb") as f:
                    content = f.read()
                await document_service.upload_and_process(
                    file_content=content,
                    filename=filename,
                    title=title,
                    description="Standard Evaluation Handbook Document",
                    category=category,
                    department="All",
                    academic_year="2026",
                    version=1,
                    uploaded_by="Evaluator"
                )
                await asyncio.sleep(1.0)

    # 2. Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "eval_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total_tests = len(dataset)
    retrieval_successes = 0
    grounding_successes = 0
    hallucination_prevention_successes = 0
    total_unanswerable = sum(1 for q in dataset if not q["is_answerable"])
    total_answerable = total_tests - total_unanswerable
    latencies = []

    print(f"\nEvaluating {total_tests} test cases ({total_answerable} answerable, {total_unanswerable} out-of-domain)...\n")

    for i, item in enumerate(dataset, 1):
        q_id = item["id"]
        question = item["question"]
        is_answerable = item["is_answerable"]
        expected_keywords = [k.lower() for k in item.get("expected_answer_keywords", [])]
        expected_doc = item.get("expected_document")

        start_time = time.time()
        result = await rag_pipeline.execute(query=question)
        duration_ms = (time.time() - start_time) * 1000
        latencies.append(duration_ms)

        answer_lower = result.answer.lower()
        retrieved_file_names = [s.get("fileName", "") for s in result.sources]

        # Check retrieval precision
        retrieval_passed = False
        if is_answerable:
            if expected_doc and expected_doc in retrieved_file_names:
                retrieval_passed = True
                retrieval_successes += 1
            elif not expected_doc and result.sources:
                retrieval_passed = True
                retrieval_successes += 1

        # Check answer grounding
        grounding_passed = False
        if is_answerable:
            matched_keywords = sum(1 for k in expected_keywords if k in answer_lower)
            if matched_keywords >= max(1, len(expected_keywords) // 2):
                grounding_passed = True
                grounding_successes += 1

        # Check hallucination rejection for out-of-domain questions
        hallucination_resisted = False
        if not is_answerable:
            if result.is_unknown or "couldn't find this information" in answer_lower:
                hallucination_resisted = True
                hallucination_prevention_successes += 1

        status_symbol = "PASS" if ((is_answerable and grounding_passed) or (not is_answerable and hallucination_resisted)) else "FAIL"
        print(f"[{i}/{total_tests}] [{status_symbol}] ({duration_ms:.1f}ms) {question}")
        if is_answerable:
            print(f"       -> Sources Retrieved: {len(result.sources)} | Top Score: {result.retrieval_score:.3f}")
        else:
            print(f"       -> Correctly Rejected as Unknown: {result.is_unknown}")

    # Summary Metrics
    print("\n" + "=" * 60)
    print("                    EVALUATION SCORECARD")
    print("=" * 60)
    
    retrieval_precision = (retrieval_successes / total_answerable) * 100 if total_answerable else 0
    answer_faithfulness = (grounding_successes / total_answerable) * 100 if total_answerable else 0
    hallucination_resistance = (hallucination_prevention_successes / total_unanswerable) * 100 if total_unanswerable else 100
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print(f"1. Retrieval Precision@K:         {retrieval_precision:.1f}% ({retrieval_successes}/{total_answerable})")
    print(f"2. Answer Grounding / Faithfulness: {answer_faithfulness:.1f}% ({grounding_successes}/{total_answerable})")
    print(f"3. Hallucination Resistance Rate: {hallucination_resistance:.1f}% ({hallucination_prevention_successes}/{total_unanswerable})")
    print(f"4. Average Response Latency:       {avg_latency:.1f} ms")
    print("=" * 60)
    
    overall_pass = (retrieval_precision >= 80.0) and (hallucination_resistance >= 90.0)
    print(f"Overall Evaluation Result: {'PASSED (EXCELLENT)' if overall_pass else 'NEEDS TUNING'}\n")
    return overall_pass

if __name__ == "__main__":
    asyncio.run(run_evaluation())
