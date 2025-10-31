const checkLoggedIn = (req, res, next) => {
    // 세션에 로그인 정보(isLoggedIn 플래그)가 있는지 확인
    if (req.session.isLoggedIn && req.session.user) {
        // 로그인 상태라면 다음 미들웨어 또는 라우터 로직으로 진행
        next(); 
    } else {
        // 로그인 상태가 아니라면 401 Unauthorized 에러 응답
        // 클라이언트에서 이 응답을 받고 로그인 페이지로 리다이렉트하게 됩니다.
        console.log('API 접근 실패: 로그인 필요');
        res.status(401).json({ error: '로그인이 필요합니다.' });
    }
};

module.exports = {
    checkLoggedIn
};
