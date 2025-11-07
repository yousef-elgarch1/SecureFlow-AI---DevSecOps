"""
Reference Policy Comparator
Compares generated policies against a reference/golden policy
"""

import re
from typing import Dict, List, Set
from collections import Counter


class ReferencePolicyComparator:
    """
    Compares generated policies against a reference/golden policy
    """

    # Key security terms to check
    SECURITY_TERMS = [
        'authentication', 'authorization', 'encryption', 'access control',
        'vulnerability', 'patch', 'update', 'secure', 'security',
        'confidentiality', 'integrity', 'availability', 'audit', 'logging',
        'monitoring', 'incident', 'response', 'recovery', 'backup',
        'firewall', 'network', 'permission', 'privilege', 'password',
        'credential', 'token', 'session', 'ssl', 'tls', 'https',
        'injection', 'xss', 'csrf', 'sql', 'sanitization', 'validation',
        'compliance', 'policy', 'procedure', 'control', 'risk',
        'threat', 'mitigation', 'prevention', 'detection', 'protection'
    ]

    # Required policy sections
    REQUIRED_SECTIONS = [
        'Executive Summary', 'Purpose', 'Scope', 'Policy Statement',
        'Risk Assessment', 'Security Controls', 'Implementation',
        'Roles and Responsibilities', 'Compliance', 'Monitoring',
        'Review', 'Enforcement', 'References'
    ]

    def compare(self, generated_policy: str, reference_policy: str) -> Dict:
        """
        Performs comprehensive comparison between generated and reference policies

        Args:
            generated_policy: The AI-generated policy text
            reference_policy: The reference/golden policy text

        Returns:
            Dict with comparison metrics
        """
        # Calculate various similarity metrics
        bleu_score = self._calculate_bleu(generated_policy, reference_policy)
        rouge_scores = self._calculate_rouge(generated_policy, reference_policy)
        key_terms = self._check_key_terms(generated_policy, reference_policy)
        structural_sim = self._compare_structure(generated_policy, reference_policy)
        length_analysis = self._analyze_length(generated_policy, reference_policy)

        # Calculate overall similarity (weighted average)
        overall_similarity = (
            bleu_score * 0.25 +
            rouge_scores['rougeL'] * 0.25 +
            (key_terms['coverage_percentage'] / 100) * 0.30 +
            (structural_sim['similarity_percentage'] / 100) * 0.20
        ) * 100

        return {
            'bleu_score': round(bleu_score, 4),
            'rouge_scores': rouge_scores,
            'key_terms_coverage': key_terms,
            'structural_similarity': structural_sim,
            'length_analysis': length_analysis,
            'overall_similarity': round(overall_similarity, 2),
            'grade': self._calculate_grade(overall_similarity)
        }

    def _calculate_bleu(self, generated: str, reference: str) -> float:
        """
        Simplified BLEU score calculation (unigram and bigram)
        """
        gen_tokens = self._tokenize(generated.lower())
        ref_tokens = self._tokenize(reference.lower())

        if not gen_tokens or not ref_tokens:
            return 0.0

        # Unigram precision
        gen_unigrams = Counter(gen_tokens)
        ref_unigrams = Counter(ref_tokens)

        overlap = sum((gen_unigrams & ref_unigrams).values())
        unigram_precision = overlap / len(gen_tokens) if gen_tokens else 0

        # Bigram precision
        gen_bigrams = Counter(zip(gen_tokens[:-1], gen_tokens[1:]))
        ref_bigrams = Counter(zip(ref_tokens[:-1], ref_tokens[1:]))

        bigram_overlap = sum((gen_bigrams & ref_bigrams).values())
        bigram_precision = bigram_overlap / len(gen_bigrams) if gen_bigrams else 0

        # Geometric mean
        if unigram_precision > 0 and bigram_precision > 0:
            bleu = (unigram_precision * bigram_precision) ** 0.5
        else:
            bleu = 0.0

        # Brevity penalty
        len_ratio = len(gen_tokens) / len(ref_tokens) if ref_tokens else 0
        if len_ratio < 1:
            bleu *= len_ratio

        return bleu

    def _calculate_rouge(self, generated: str, reference: str) -> Dict:
        """
        Simplified ROUGE-1, ROUGE-2, and ROUGE-L calculation
        """
        gen_tokens = self._tokenize(generated.lower())
        ref_tokens = self._tokenize(reference.lower())

        # ROUGE-1 (unigram overlap)
        gen_unigrams = set(gen_tokens)
        ref_unigrams = set(ref_tokens)

        overlap = len(gen_unigrams & ref_unigrams)
        rouge1_precision = overlap / len(gen_unigrams) if gen_unigrams else 0
        rouge1_recall = overlap / len(ref_unigrams) if ref_unigrams else 0
        rouge1_f1 = (2 * rouge1_precision * rouge1_recall) / (rouge1_precision + rouge1_recall) if (rouge1_precision + rouge1_recall) > 0 else 0

        # ROUGE-2 (bigram overlap)
        gen_bigrams = set(zip(gen_tokens[:-1], gen_tokens[1:]))
        ref_bigrams = set(zip(ref_tokens[:-1], ref_tokens[1:]))

        bigram_overlap = len(gen_bigrams & ref_bigrams)
        rouge2_precision = bigram_overlap / len(gen_bigrams) if gen_bigrams else 0
        rouge2_recall = bigram_overlap / len(ref_bigrams) if ref_bigrams else 0
        rouge2_f1 = (2 * rouge2_precision * rouge2_recall) / (rouge2_precision + rouge2_recall) if (rouge2_precision + rouge2_recall) > 0 else 0

        # ROUGE-L (longest common subsequence)
        lcs_length = self._lcs_length(gen_tokens, ref_tokens)
        rougeL_precision = lcs_length / len(gen_tokens) if gen_tokens else 0
        rougeL_recall = lcs_length / len(ref_tokens) if ref_tokens else 0
        rougeL_f1 = (2 * rougeL_precision * rougeL_recall) / (rougeL_precision + rougeL_recall) if (rougeL_precision + rougeL_recall) > 0 else 0

        return {
            'rouge1': round(rouge1_f1, 4),
            'rouge2': round(rouge2_f1, 4),
            'rougeL': round(rougeL_f1, 4)
        }

    def _check_key_terms(self, generated: str, reference: str) -> Dict:
        """
        Extracts key security terms from reference and checks coverage in generated policy
        """
        gen_lower = generated.lower()
        ref_lower = reference.lower()

        # Extract security terms present in reference
        reference_terms = set()
        for term in self.SECURITY_TERMS:
            if term in ref_lower:
                reference_terms.add(term)

        # Check which terms are also in generated policy
        generated_terms = set()
        for term in reference_terms:
            if term in gen_lower:
                generated_terms.add(term)

        missing_terms = reference_terms - generated_terms

        # Extract additional terms from reference (nouns/important words)
        ref_additional = self._extract_important_words(reference)
        gen_additional = self._extract_important_words(generated)

        additional_overlap = len(ref_additional & gen_additional)
        additional_coverage = (additional_overlap / len(ref_additional) * 100) if ref_additional else 0

        return {
            'reference_terms_count': len(reference_terms),
            'generated_terms_count': len(generated_terms),
            'overlap_count': len(generated_terms),
            'coverage_percentage': round((len(generated_terms) / len(reference_terms) * 100) if reference_terms else 0, 1),
            'missing_terms': sorted(list(missing_terms)),
            'covered_terms': sorted(list(generated_terms)),
            'additional_important_words': {
                'reference_count': len(ref_additional),
                'generated_count': len(gen_additional),
                'overlap': additional_overlap,
                'coverage_percentage': round(additional_coverage, 1)
            }
        }

    def _compare_structure(self, generated: str, reference: str) -> Dict:
        """
        Compares document structure (sections present)
        """
        gen_sections = self._extract_sections(generated)
        ref_sections = self._extract_sections(reference)

        # Check for required sections
        gen_has_required = set()
        ref_has_required = set()

        for section in self.REQUIRED_SECTIONS:
            section_lower = section.lower()
            if any(section_lower in s.lower() for s in gen_sections):
                gen_has_required.add(section)
            if any(section_lower in s.lower() for s in ref_sections):
                ref_has_required.add(section)

        missing_sections = ref_has_required - gen_has_required
        extra_sections = gen_has_required - ref_has_required

        similarity = (len(gen_has_required & ref_has_required) / len(ref_has_required) * 100) if ref_has_required else 0

        return {
            'reference_sections': sorted(list(ref_sections)),
            'generated_sections': sorted(list(gen_sections)),
            'reference_section_count': len(ref_sections),
            'generated_section_count': len(gen_sections),
            'common_sections': sorted(list(gen_has_required & ref_has_required)),
            'missing_sections': sorted(list(missing_sections)),
            'extra_sections': sorted(list(extra_sections)),
            'similarity_percentage': round(similarity, 1)
        }

    def _analyze_length(self, generated: str, reference: str) -> Dict:
        """
        Analyzes length comparison
        """
        gen_words = len(self._tokenize(generated))
        ref_words = len(self._tokenize(reference))

        gen_lines = len(generated.split('\n'))
        ref_lines = len(reference.split('\n'))

        length_ratio = (gen_words / ref_words) if ref_words > 0 else 0

        return {
            'generated_words': gen_words,
            'reference_words': ref_words,
            'word_ratio': round(length_ratio, 2),
            'generated_lines': gen_lines,
            'reference_lines': ref_lines,
            'line_ratio': round((gen_lines / ref_lines) if ref_lines > 0 else 0, 2),
            'length_assessment': self._assess_length(length_ratio)
        }

    def _assess_length(self, ratio: float) -> str:
        """Provides assessment of length appropriateness"""
        if ratio < 0.5:
            return "Too short - Generated policy is significantly shorter than reference"
        elif ratio < 0.8:
            return "Somewhat short - Consider adding more detail"
        elif ratio <= 1.2:
            return "Appropriate length - Similar to reference policy"
        elif ratio <= 1.5:
            return "Somewhat long - Consider condensing"
        else:
            return "Too long - Generated policy is significantly longer than reference"

    def _calculate_grade(self, score: float) -> str:
        """Convert similarity score to letter grade"""
        if score >= 90:
            return "A (Excellent similarity)"
        elif score >= 80:
            return "B (Good similarity)"
        elif score >= 70:
            return "C (Moderate similarity)"
        elif score >= 60:
            return "D (Low similarity)"
        else:
            return "F (Poor similarity)"

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Remove special characters and split on whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        return [word for word in text.split() if len(word) > 1]

    def _lcs_length(self, seq1: List, seq2: List) -> int:
        """Longest Common Subsequence length"""
        if not seq1 or not seq2:
            return 0

        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        return dp[m][n]

    def _extract_sections(self, text: str) -> Set[str]:
        """Extract section headers from policy text"""
        sections = set()

        # Look for common section header patterns
        # Pattern 1: Lines that start with capital letters and end with colon
        pattern1 = r'^([A-Z][A-Za-z\s]+):\s*$'

        # Pattern 2: Lines in all caps
        pattern2 = r'^([A-Z\s]{3,})$'

        # Pattern 3: Numbered sections like "1. Introduction" or "1.1 Purpose"
        pattern3 = r'^\d+\.?\d*\s+([A-Z][A-Za-z\s]+)'

        for line in text.split('\n'):
            line = line.strip()

            match1 = re.match(pattern1, line)
            match2 = re.match(pattern2, line)
            match3 = re.match(pattern3, line)

            if match1:
                sections.add(match1.group(1).strip())
            elif match2 and len(line) < 50:  # Not too long to be a section header
                sections.add(line.strip())
            elif match3:
                sections.add(match3.group(1).strip())

        return sections

    def _extract_important_words(self, text: str) -> Set[str]:
        """Extract important words (longer than 5 chars, not common words)"""
        common_words = {
            'about', 'above', 'after', 'again', 'against', 'all', 'among', 'and',
            'any', 'are', 'because', 'been', 'before', 'being', 'below', 'between',
            'both', 'but', 'by', 'can', 'did', 'do', 'does', 'doing', 'down',
            'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has',
            'have', 'having', 'here', 'how', 'if', 'in', 'into', 'is', 'it',
            'its', 'itself', 'more', 'most', 'no', 'nor', 'not', 'now', 'of',
            'off', 'on', 'once', 'only', 'or', 'other', 'out', 'over', 'own',
            'same', 'should', 'so', 'some', 'such', 'than', 'that', 'the',
            'their', 'them', 'then', 'there', 'these', 'they', 'this', 'those',
            'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was',
            'were', 'what', 'when', 'where', 'which', 'while', 'who', 'will',
            'with', 'would', 'your'
        }

        words = self._tokenize(text.lower())
        important = set()

        for word in words:
            if len(word) > 5 and word not in common_words:
                important.add(word)

        return important

    def generate_report(self, comparison: Dict) -> str:
        """
        Generates human-readable comparison report

        Args:
            comparison: Output from compare()

        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 80)
        report.append("REFERENCE POLICY COMPARISON REPORT")
        report.append("=" * 80)
        report.append("")

        # Overall similarity
        report.append(f"Overall Similarity: {comparison['overall_similarity']}%")
        report.append(f"Grade: {comparison['grade']}")
        report.append("")

        # BLEU Score
        report.append("-" * 80)
        report.append("BLEU Score (Text Similarity)")
        report.append("-" * 80)
        report.append(f"Score: {comparison['bleu_score']:.4f} ({comparison['bleu_score'] * 100:.2f}%)")
        report.append("")

        # ROUGE Scores
        report.append("-" * 80)
        report.append("ROUGE Scores (Content Overlap)")
        report.append("-" * 80)
        rouge = comparison['rouge_scores']
        report.append(f"ROUGE-1 (Unigram):  {rouge['rouge1']:.4f} ({rouge['rouge1'] * 100:.2f}%)")
        report.append(f"ROUGE-2 (Bigram):   {rouge['rouge2']:.4f} ({rouge['rouge2'] * 100:.2f}%)")
        report.append(f"ROUGE-L (LCS):      {rouge['rougeL']:.4f} ({rouge['rougeL'] * 100:.2f}%)")
        report.append("")

        # Key Terms Coverage
        report.append("-" * 80)
        report.append("Key Security Terms Coverage")
        report.append("-" * 80)
        terms = comparison['key_terms_coverage']
        report.append(f"Coverage: {terms['overlap_count']}/{terms['reference_terms_count']} terms ({terms['coverage_percentage']}%)")
        report.append("")

        if terms['covered_terms']:
            report.append(f"[+] Covered Terms ({len(terms['covered_terms'])}):")
            report.append("  " + ", ".join(terms['covered_terms']))
            report.append("")

        if terms['missing_terms']:
            report.append(f"[-] Missing Terms ({len(terms['missing_terms'])}):")
            report.append("  " + ", ".join(terms['missing_terms']))
            report.append("")

        # Structural Similarity
        report.append("-" * 80)
        report.append("Document Structure Comparison")
        report.append("-" * 80)
        struct = comparison['structural_similarity']
        report.append(f"Similarity: {struct['similarity_percentage']}%")
        report.append(f"Reference has {struct['reference_section_count']} sections")
        report.append(f"Generated has {struct['generated_section_count']} sections")
        report.append("")

        if struct['common_sections']:
            report.append(f"[+] Common Sections ({len(struct['common_sections'])}):")
            for section in struct['common_sections']:
                report.append(f"  - {section}")
            report.append("")

        if struct['missing_sections']:
            report.append(f"[-] Missing Sections ({len(struct['missing_sections'])}):")
            for section in struct['missing_sections']:
                report.append(f"  - {section}")
            report.append("")

        if struct['extra_sections']:
            report.append(f"[*] Extra Sections ({len(struct['extra_sections'])}):")
            for section in struct['extra_sections']:
                report.append(f"  - {section}")
            report.append("")

        # Length Analysis
        report.append("-" * 80)
        report.append("Length Analysis")
        report.append("-" * 80)
        length = comparison['length_analysis']
        report.append(f"Reference: {length['reference_words']} words, {length['reference_lines']} lines")
        report.append(f"Generated: {length['generated_words']} words, {length['generated_lines']} lines")
        report.append(f"Ratio: {length['word_ratio']:.2f}x")
        report.append(f"Assessment: {length['length_assessment']}")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Test with sample policies
    reference = """
    SECURITY POLICY FOR SQL INJECTION PREVENTION

    Executive Summary:
    This policy addresses the prevention of SQL injection vulnerabilities through proper input validation, parameterized queries, and secure coding practices.

    Risk Assessment:
    SQL injection attacks can lead to unauthorized access, data breaches, and system compromise.

    Security Controls:
    - Use parameterized queries with prepared statements
    - Implement input validation and sanitization
    - Apply principle of least privilege for database access
    - Enable security monitoring and logging

    Implementation:
    All developers must use ORM frameworks or parameterized queries. Code reviews must verify proper implementation.

    Roles and Responsibilities:
    Development team is responsible for secure coding. Security team conducts audits.

    Compliance:
    This policy maps to NIST CSF PR.AC-4 and ISO 27001 A.14.2.5.

    Monitoring:
    Security team will monitor for SQL injection attempts using WAF and SIEM.
    """

    generated = """
    SQL INJECTION PREVENTION POLICY

    Purpose:
    Prevent SQL injection vulnerabilities in our applications.

    Risk:
    SQL injection can compromise data integrity and confidentiality.

    Controls:
    - Always use parameterized queries
    - Validate all user input
    - Use least privilege database accounts
    - Log all database access

    Implementation:
    Developers must follow secure coding guidelines. Regular security testing required.

    Compliance:
    Maps to NIST CSF PR.AC-4, ISO 27001 A.14.2.5.
    """

    comparator = ReferencePolicyComparator()
    result = comparator.compare(generated, reference)

    print(comparator.generate_report(result))
    print("\nJSON Output:")
    import json
    print(json.dumps(result, indent=2))
