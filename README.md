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
- 전체 변경 이력: [`manuscript-proofreading/README.md` § Changelog](manuscript-proofreading/README.md#changelog)

## How it works (v2.2.0+)

기본 실행 방식은 **6개 전문 페르소나의 병렬 검토**입니다 — 숫자·통계 일관성, 표/그림 구조,
용어·임상적 방향성, Methods–Results 일치성, 전/후반부 및 참고문헌, 일반 교정·ACP 하우스스타일을
각각 담당하는 서브에이전트를 동시에 띄운 뒤(Claude Code의 `Agent` 도구 등 서브에이전트 디스패치가
가능한 환경에서), 하나의 코디네이터가 결과를 병합·중복 제거·최종 크로스체크하여 단일 결과물을
냅니다. 서브에이전트 디스패치가 불가능한 환경(예: ChatGPT Custom GPT)에서는 동일한 6개 페르소나를
순차적으로 시뮬레이션합니다. 자세한 실행 흐름은
[`manuscript-proofreading/SKILL.md`](manuscript-proofreading/SKILL.md)의 "Execution mode" /
"Reviewer personas" 섹션을 참고하세요.

전/후반부·참고문헌 담당 페르소나는 기본적으로 참고문헌 23건 등 모든 항목을 웹 검색(PubMed/
CrossRef/Google Scholar 등)으로 대조하여 실존 여부와 서지정보 일치를 확인합니다.

## Authors

- **이수영 (Soo Young Lee)** — 전남대학교 의과대학 대장항문외과. 원저자 (initial design and implementation).
- **강상희 (Sanghee Kang)** — 고려대학교 의과대학. 수정 및 개선 (v2.0.0: checker robustness, tests,
  cross-platform packaging; v2.1.0: parallel reviewer-persona execution; v2.2.0: default
  reference-existence verification).

## Packaging

Claude.ai 업로드용 패키지 생성: `zip -r manuscript-proofreading.skill manuscript-proofreading`
