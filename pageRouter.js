const express = require('express');
const router = express.Router();
const path = require('path');

// ------------------------------------------------------------------
// GET / : 메인 페이지 (세션 상태에 따라 메뉴 변경)
// ------------------------------------------------------------------
router.get('/', (req, res) => {
    // 1. 세션 정보 확인
    const user = req.session.user;

    // 2. 로그인 여부에 따른 상태 메시지 및 메뉴 HTML 생성
    let loginStatusHTML = '';
    let menuHTML = '';

    if (user) {
        // [로그인 상태]
        loginStatusHTML = `<strong>${user.nick}</strong>님 환영합니다! (${user.user_id})`;
        menuHTML = `
            <a href="/update.html">회원정보 수정 페이지</a> |
            <a href="/delete.html">회원탈퇴 페이지</a> |
            <a href="/disinfestation.html">방제 기록 등록</a> |
            <a href="/pest_register.html">병해충 정보 등록</a> |
            <a href="/post_register.html">커뮤니티 글쓰기</a> |
            <a href="/comment_register.html">댓글 등록</a> |
            <a href="/db/logout">로그아웃</a>
        `;
    } else {
        // [로그아웃 상태]
        loginStatusHTML = `로그인이 필요합니다.`;
        menuHTML = `
            <a href="/register.html">회원가입 페이지</a> |
            <a href="/login.html">로그인 페이지</a> |
            <a href="/update.html">회원정보 수정 페이지</a> |
            <a href="/delete.html">회원탈퇴 페이지</a> |
            <a href="/disinfestation.html">방제 기록 등록</a> |
            <a href="/pest_register.html">병해충 정보 등록</a> |
            <a href="/post_register.html">커뮤니티 글쓰기</a> |
            <a href="/comment_register.html">댓글 등록</a>
        `;
    }

    // 3. HTML 템플릿 응답
    const mainPageHTML = `
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>뉴턴사과 메인</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <h1>회원관리 시스템입니다.</h1>
            <p>${loginStatusHTML}</p>
            <p>원하는 기능을 선택하세요.</p>
            <div id="menu">
                ${menuHTML}
            </div>
        </body>
        </html>
    `;

    res.send(mainPageHTML);
});


// ------------------------------------------------------------------
// GET /:filename : public 폴더의 HTML 파일에 대한 요청을 처리 (기존 유지)
// ------------------------------------------------------------------

router.get('/:filename', (req, res, next) => {
    const filename = req.params.filename;
    
    if (!filename.endsWith('.html')) {
        return next();
    }
    
    const filePath = path.join(__dirname, '..', 'public', filename);
    res.sendFile(filePath, (err) => {
        if (err) {
            console.error(err);
            res.status(404).send('404 Not Found: 요청하신 페이지를 찾을 수 없습니다.');
        }
    });
});

module.exports = router;
