"""
Evaluation Metrics for Generated Security Policies
Implements BLEU and ROUGE-L scores for comparative LLM study
"""

import re
from typing import List, Dict
from collections import Counter
import math


class PolicyEvaluationMetrics:
    """Calculate BLEU and ROUGE-L metrics for policy quality assessment"""

    @staticmethod
    def calculate_bleu(
        candidate: str,
        reference: str,
        max_n: int = 4
    ) -> Dict[str, float]:
        """
        Calculate BLEU score (Bilingual Evaluation Understudy)
        Measures n-gram precision between candidate and reference text

        Args:
            candidate: Generated policy text
            reference: Reference policy text
            max_n: Maximum n-gram size (default: 4 for BLEU-4)

        Returns:
            Dict with BLEU scores for n=1,2,3,4 and overall BLEU-4
        """
        # Tokenize (simple whitespace split + lowercase)
        candidate_tokens = candidate.lower().split()
        reference_tokens = reference.lower().split()

        # Calculate brevity penalty
        c = len(candidate_tokens)
        r = len(reference_tokens)

        if c == 0:
            return {'bleu-1': 0.0, 'bleu-2': 0.0, 'bleu-3': 0.0, 'bleu-4': 0.0}

        if c > r:
            bp = 1.0
        else:
            bp = math.exp(1 - r / c)

        # Calculate n-gram precisions
        precisions = []

        for n in range(1, max_n + 1):
            candidate_ngrams = PolicyEvaluationMetrics._get_ngrams(candidate_tokens, n)
            reference_ngrams = PolicyEvaluationMetrics._get_ngrams(reference_tokens, n)

            if not candidate_ngrams:
                precisions.append(0.0)
                continue

            # Count matches
            matches = 0
            for ngram, count in candidate_ngrams.items():
                matches += min(count, reference_ngrams.get(ngram, 0))

            precision = matches / sum(candidate_ngrams.values())
            precisions.append(precision)

        # Calculate geometric mean of precisions
        if all(p > 0 for p in precisions):
            log_precisions = [math.log(p) for p in precisions]
            geo_mean = math.exp(sum(log_precisions) / len(log_precisions))
        else:
            geo_mean = 0.0

        bleu_score = bp * geo_mean

        return {
            'bleu-1': precisions[0] if len(precisions) > 0 else 0.0,
            'bleu-2': precisions[1] if len(precisions) > 1 else 0.0,
            'bleu-3': precisions[2] if len(precisions) > 2 else 0.0,
            'bleu-4': bleu_score,
            'brevity_penalty': bp,
            'length_ratio': c / r if r > 0 else 0.0
        }

    @staticmethod
    def calculate_rouge_l(
        candidate: str,
        reference: str
    ) -> Dict[str, float]:
        """
        Calculate ROUGE-L score (Recall-Oriented Understudy for Gisting Evaluation)
        Measures longest common subsequence between candidate and reference

        Args:
            candidate: Generated policy text
            reference: Reference policy text

        Returns:
            Dict with ROUGE-L precision, recall, and F1 score
        """
        # Tokenize
        candidate_tokens = candidate.lower().split()
        reference_tokens = reference.lower().split()

        if not candidate_tokens or not reference_tokens:
            return {'rouge-l-precision': 0.0, 'rouge-l-recall': 0.0, 'rouge-l-f1': 0.0}

        # Calculate LCS (Longest Common Subsequence)
        lcs_length = PolicyEvaluationMetrics._lcs_length(candidate_tokens, reference_tokens)

        # Calculate precision, recall, F1
        precision = lcs_length / len(candidate_tokens) if candidate_tokens else 0.0
        recall = lcs_length / len(reference_tokens) if reference_tokens else 0.0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        return {
            'rouge-l-precision': precision,
            'rouge-l-recall': recall,
            'rouge-l-f1': f1,
            'lcs_length': lcs_length
        }

    @staticmethod
    def _get_ngrams(tokens: List[str], n: int) -> Counter:
        """Extract n-grams from token list"""
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i + n])
            ngrams.append(ngram)
        return Counter(ngrams)

    @staticmethod
    def _lcs_length(seq1: List[str], seq2: List[str]) -> int:
        """Calculate length of longest common subsequence"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

    @staticmethod
    def evaluate_policy(
        generated_policy: str,
        reference_policy: str
    ) -> Dict[str, float]:
        """Complete evaluation of generated policy against reference"""
        bleu_scores = PolicyEvaluationMetrics.calculate_bleu(generated_policy, reference_policy)
        rouge_scores = PolicyEvaluationMetrics.calculate_rouge_l(generated_policy, reference_policy)
        return {**bleu_scores, **rouge_scores}

    @staticmethod
    def compare_llm_outputs(
        llm_outputs: Dict[str, str],
        reference: str
    ) -> Dict[str, Dict[str, float]]:
        """Compare multiple LLM outputs against a reference"""
        results = {}
        for llm_name, output in llm_outputs.items():
            results[llm_name] = PolicyEvaluationMetrics.evaluate_policy(output, reference)
        return results


# Test function
if __name__ == "__main__":
    print("="*60)
    print("POLICY EVALUATION METRICS TEST")
    print("="*60)

    reference = "SQL injection prevention requires parameterized queries. NIST CSF PR.DS-5. ISO 27001 A.14.2.5. Fix within 48 hours."
    generated = "SQL injection mitigation uses prepared statements. NIST PR.DS-5. ISO A.14.2.5. Timeline: 48 hours."

    print("\nBLEU Score:")
    bleu = PolicyEvaluationMetrics.calculate_bleu(generated, reference)
    print(f"  BLEU-4: {bleu['bleu-4']:.4f}")

    print("\nROUGE-L Score:")
    rouge = PolicyEvaluationMetrics.calculate_rouge_l(generated, reference)
    print(f"  ROUGE-L F1: {rouge['rouge-l-f1']:.4f}")

    print("\nTest completed successfully!")
