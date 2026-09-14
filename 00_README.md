# 01 CROWNY Skin

원본 시안의 큰 CROWNY 워드마크, 유리 왕관 히어로, 건축·조형물 화보와 아이보리 배경을 이어가는 반응형 쇼핑몰 디자인입니다. 상세·장바구니·주문 화면은 정보 사이 여백을 넓혀 차분하게 구성했습니다.

## 열어보기

ZIP을 풀고 `01_CROWNY_Skin/index.html`을 브라우저에서 여세요. HTML과 `assets` 폴더를 함께 보관하세요. 설치나 빌드가 필요하지 않습니다. 웹폰트·Swiper·사진도 로컬 파일입니다.

## 페이지 구성

| 파일 | 화면 |
| --- | --- |
| index.html | 히어로 3장, 카테고리, 추천 8개, 신상품 8개, 베스트 8개, 띠배너 2개, 브랜드 이야기 |
| products.html | 상품 16개, 분류·검색·정렬, 페이지네이션 모양 |
| product-detail.html | 1번 상품 상세 |
| product-detail-02.html ~ product-detail-16.html | 2~16번 상품별 상세 |
| brand.html / lookbook.html | 브랜드 소개 / 화보·갤러리 |
| cart.html / checkout.html | 장바구니 / 주문·결제 화면 |
| login.html / signup.html | 로그인 / 회원가입 화면 |
| notice.html / notice-detail.html | 공지 목록 / 공지 상세 |
| reviews.html / review-write.html | 리뷰 목록 / 리뷰 작성 화면 |
| qna.html / qna-detail.html / qna-write.html | 문의 목록 / 상세 / 작성 화면 |
| faq.html / events.html / contact.html | FAQ / 이벤트·팝업 / 고객센터 |
| terms.html / privacy.html | 운영자가 정책 내용을 넣을 자리 |

총 53개 HTML입니다. 원본에서 확인한 상품·브랜드 분류·리뷰 발췌를 별도 카탈로그와 상세 화면으로 연결했고, 디자인 예시 상품도 유지했습니다. 원본 접근이 제한된 항목은 원문 링크와 ‘미이관’ 상태를 표시합니다.

## 이미지

모든 사진은 이 디자인을 위해 AI로 생성한 실사 스타일 이미지이며, 임시 이미지 주소를 사용하지 않습니다.

| 파일 | 크기 | 수량 |
| --- | --- | --- |
| assets/images/hero-01.jpg ~ hero-03.jpg | 2000 × 900 | 3 |
| assets/images/banner-01.jpg ~ banner-02.jpg | 2000 × 500 | 2 |
| assets/images/popup-01.jpg ~ popup-02.jpg | 400 × 300 | 2 |
| assets/images/product-01.jpg ~ product-16.jpg | 600 × 600 | 16 |
| assets/images/detail-01.jpg ~ detail-16.jpg | 800 × 3000 | 16 |
| assets/images/mission.jpg | 1600 × 1000 | 1 |

상품 이미지는 마지막 요청의 600 × 600 규격을 적용했습니다. 상세 캠페인 이미지는 원본 사진의 비율을 유지하고 여백을 포함해 800 × 3000으로 내보냈습니다. 이미지 속 글씨는 이미지 편집이 필요하며, 제품 설명과 정보표는 HTML에서도 수정할 수 있습니다. 카테고리 썸네일은 해당 상품 사진을 재사용합니다. 팝업 두 개는 `events.html`에서 버튼으로 확인합니다.

## 스타일 수정

각 HTML의 `<head><style>` 안에 동일한 테마가 들어 있습니다. 공통 스타일을 바꿀 때는 모든 HTML에 동일하게 적용하세요. 외부 CSS 파일은 없습니다.

| 변수 | 용도 / 기본값 |
| --- | --- |
| --main | 주요 글자색 / #171917 |
| --sub | 보조 글자색 / #777b75 |
| --point | 모든 강조색 / #344d40 |
| --bg / --surface / --line | 배경 / 이미지 바탕 / 구분선 |
| --font-body / --font-display | Noto Sans KR / Archivo Black |
| --font-h1 / --font-h2 / --font-h3 | 제목 계층 크기 |
| --font-body-size / --font-small / --text-* | 본문·세부 글자 크기 |
| --weight-regular / --weight-medium / --weight-bold | 글자 두께 400 / 500 / 700 |
| --section-gap / --section-gap-small | 섹션 간격 120px / 64px |
| --page-padding / --card-gap | 좌우 여백 40px / 상품 간격 24px |
| --content-width / --subpage-width | 최대 콘텐츠 폭 1500px |
| --radius / --radius-card / --radius-control | 모서리 8px |

1100px 이하와 760px 이하의 미디어쿼리에서 여백·크기를 조정합니다. 모바일 상품은 2열입니다. 히어로는 화면 폭을 사용하고 일반 콘텐츠는 최대 1500px에 맞춥니다.

## 섹션 순서와 이미지 교체

`index.html`의 `hero`, `categories`, `recommended`, `new`, `best`, `promo-one`, `promo-two`는 각각 독립 `<section>`입니다. 주석의 START~END 영역을 통째로 옮기면 순서를 바꿀 수 있습니다. 숨기려면 해당 `<section>`에 `hidden` 속성을 넣으세요.

이미지는 모두 `<img src="assets/images/파일명.jpg">`입니다. 같은 파일명으로 교체하거나 `src`를 수정하면 됩니다. 상품 카드는 `<li class="item">`을 직접 복사·편집하세요. 상품 카드와 메뉴를 런타임 JS로 생성하지 않습니다.

## 움직임과 UI 범위

스크롤 등장은 IntersectionObserver와 CSS의 fade·slide-up입니다. 등장 후 한 번만 표시하며, 사용자의 동작 줄이기 설정을 존중합니다. 메인 페이지의 데스크톱 휠에는 바닐라 JS 감속 스크롤을 적용했습니다. 모바일 터치·키보드·입력창·내부 스크롤 영역·열린 팝업에서는 기본 스크롤을 유지합니다. 메인 외 페이지는 기존 기본 스크롤을 유지합니다. 히어로는 Swiper 12.2.0으로 6초마다 전환하며 화살표·페이지 표시·재생 정지 버튼이 있습니다.

상세페이지의 카드뉴스는 우측 하단 관리자 설정에서 세로/가로, 부드러운 이동 여부를 선택할 수 있습니다. 설정은 `CrownySettings` 어댑터로 분리되어 있어 향후 카페24 관리자나 별도 디자인관리 앱의 load/save API에 연결할 수 있습니다. 커뮤니티 글은 스크롤 위치를 기준으로 글자가 즉시 채워져 타이핑을 기다리지 않습니다. 상품 상세의 CROWNY WORLD 버튼은 국가별 사용 맥락 패널을 엽니다.

메뉴, 탭, 팝업, 정렬, 체크박스, 수량·합계 변경은 화면 확인용입니다. 실제 장바구니 데이터, 주문 전달, 결제, 회원 인증, 게시글 저장은 구현하지 않았습니다. 펀딩 신청 화면은 정적 스킨만으로 개인정보를 저장하지 않으며, 동봉된 `server/app.py`를 HTTPS 서버로 운영하고 관리자 설정에서 접수 동의를 켠 경우에만 신청자 저장 API를 사용할 수 있습니다. 서버 운영 시 `CROWNY_ADMIN_PASSWORD`(12자 이상)와 `CROWNY_DATA_DIR`를 별도 환경변수로 지정하세요.

## 카페24 적용

이 결과물은 요청한 정적 HTML/CSS 디자인 원본입니다. 카페24 모듈·상품 변수·주문 및 회원 기능에 연결된 자동 설치 스킨은 아닙니다. 적용 시 카드와 옵션·주문·게시판 영역을 카페24의 해당 모듈과 변수에 연결하고 기존 이벤트와 예시 UI 이벤트의 중복을 정리하세요. 사업자 정보, 정책, 실제 판매 데이터도 운영 정보로 교체하세요.

## 확인 범위

`01_QA_REPORT.md`에 파일·이미지·공통 레이아웃과 UI 동작 검사 결과를 정리했습니다. 실제 카페24 환경 및 데스크톱·모바일 브라우저에서 최종 시각 검수는 별도로 필요합니다.

폰트 및 Swiper 라이선스는 `licenses` 폴더에 포함했습니다.


메인 모션 추가 사항과 조절 방법은 `02_MOTION.md`를 확인하세요.
