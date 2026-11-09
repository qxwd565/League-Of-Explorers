# League Of Explorers — HSdeck API

이 저장소는 `qxwd565/legacy`와 동일한 **schema 1** API 파일 형식으로 만들어졌습니다. 시간 기준은 **Asia/Seoul(한국 날짜)**입니다.

- `cards.json`: 현재 카드 데이터(원화 경로 `art`는 항상 `""`)
- `render.json`: 현재 데이터와 날짜별 과거 변경값을 합친 WebGL 전용 API
- `history.json`: 이전 HScard 플러그인을 위한 호환 인덱스
- `data/<카드ID>.json`: 원본 카드 정보 + `card`에 최초 스펙을 저장하고 `card.patches`에는 후속 변경된 필드만 기록
- `release-policy.json`: 확장팩·미니세트·선행 카드 출시일
- `manifest.json`: 데이터 수량 및 검증 범위
- `art/`, `golden/`: 이미지 없이 `.gitkeep`만 보관. 이미지를 나중에 추가할 때 **카드 ID 파일명을 쓰지 않고 원화 내용 SHA-256 해시 파일명을 사용**합니다.

## 이번 작업

- 고유 카드 원본 60건, 수집 가능 45장, 수집 불가 15건
- 생성형 카드 조합 변형 0건은 별도 `data/combinations/`에 보관(같은 카드 ID 중복 등록 방지)
- 검증된 패치 변경 필드가 기록된 카드 1장 / 변경 날짜 이벤트 1건
- 출시일 미확정 카드 0건
- 카드 이미지 **0개 업로드**

> 주의: 제공된 ZIP에는 현재 카드 스펙만 있습니다. *최초 등장 당시의 값*은 공식 변경 이력이 확인된 필드만 역산했으며, 다른 필드는 원본에 과거 값이 없어 최신 수치로 임시 채웠습니다. 이를 `card.initialSpecStatus`로 기록했습니다. 미확인 초기 스펙을 검증된 과거 사실로 오해하지 마세요. 날짜별 `card.history`도 검증된 변경 사항에 대해서만 신뢰할 수 있습니다.

카드 이름이 아닌 **정확한 카드 ID/dbfId를 기준**으로 변경 이력을 연결했습니다.

**기존 저장소의 원화·황금 애니메이션 자료 및 이미지 경로는 수정하거나 삭제하지 않았습니다.**


## Date-first history

See [date-schema.md](docs/date-schema.md) for the 62 per-card timelines, 60-card compatible/precise root endpoints, pinned source provenance, Korean date policy, validation commands and explicit uncertainty. The old root endpoints remain schema 1; use the `-date.json` siblings only with a historySchema 2 capable reader. No live plugin settings were changed.
