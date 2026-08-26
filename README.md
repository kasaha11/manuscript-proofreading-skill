# manuscript-proofreading-skill

**Annals of Coloproctology (ACP)** 게재 확정(accepted) 원고의 출판 전 최종 교정(proofreading)을
위한 에이전트 스킬입니다. 수치·통계 일관성, 표/그림 구조, Methods–Results 일치, ACP house style을
점검하고 PDF에 바로 붙여넣을 수 있는 코멘트를 생성합니다. Claude, OpenAI Codex, 그리고
Custom GPT를 통해 ChatGPT에서 사용할 수 있습니다.

An agent skill for final-stage proofreading of accepted manuscripts for the
*Annals of Coloproctology* (ACP): numerical/statistical consistency, table and
figure structure, Methods–Results agreement, and ACP house style, producing
PDF-ready annotation comments.

- GitHub: https://github.com/kasaha11/manuscript-proofreading-skill
- 플랫폼별 설치 방법: [`manuscript-proofreading/README.md`](manuscript-proofreading/README.md)

## Authors

- **이수영 (Soo Young Lee)** — 전남대학교 의과대학 대장항문외과. 원저자 (initial design and implementation).
- **강상희 (Sanghee Kang)** — 고려대학교 의과대학. 수정 및 개선 (v2.0.0: checker robustness, tests, cross-platform packaging).

## Packaging

Claude.ai 업로드용 패키지 생성: `zip -r manuscript-proofreading.skill manuscript-proofreading`
