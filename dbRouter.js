const express = require('express');
const router = express.Router();
const db = require('../config/db'); // Promise 기반 DB 연결 (config/db.js 수정 가정)

// ------------------------------------------------------------------
// POST /db/register: 회원가입 처리
// ------------------------------------------------------------------
router.post('/register', async (req, res) => {
    // 1. 클라이언트 데이터 받기
    const { user_id, pwd, nick, farm_region } = req.body;

    console.log(`✅✅✅ /db/register 라우터 진입 성공! ✅✅✅`);
    console.log('클라이언트에서 받은 데이터 (req.body):', req.body);

    // 2. DB 쿼리 실행
const sql = 'INSERT INTO tb_user (user_id, pwd, nick, farm_region, joined_at) VALUES (?, ?, ?, ?, NOW())';

    // 🚨 현재는 평문 비밀번호를 사용하지만, 실제 서비스에서는 보안을 위해 반드시 해싱을 사용해야 합니다.
    const values = [user_id, pwd, nick, farm_region]; 

    try {
    const [rows, fields] = await db.query(sql, values);

     console.log('DB 회원가입 성공:', rows);
    //  res.redirect('/'); 

        res.json({
        success: true,
        message: "회원가입이 성공적으로 완료되었습니다. 로그인 페이지로 이동합니다.",
        redirect: '/'
         });

        } catch (error) {
         console.error('DB 회원가입 오류:', error);

        res.status(500).json({
            success: false,
            message: "서버 오류가 발생했습니다."
         });
        //   res.redirect('/'); 
    }
});

// ------------------------------------------------------------------
// POST /db/login: 로그인 처리
// ------------------------------------------------------------------
router.post('/login', async (req, res) => {

     const { id, pw } = req.body; 

    console.log(`🚀🚀🚀 /db/login 라우터 진입! 🚀🚀🚀`);
     console.log('로그인 시도 데이터:', { id, pw });


     const sql = 'SELECT * FROM tb_user WHERE user_id = ?';
     const values = [id];

     try {
         const [rows] = await db.query(sql, values);


         if (rows.length === 0) {
         console.log('로그인 실패: 존재하지 않는 아이디');
         return res.send('<script>alert("존재하지 않는 아이디입니다."); location.href="/login.html";</script>');
        }

         const user = rows[0];

         if (pw === user.pwd) { 

             req.session.isLogin = true;
             req.session.user = {
             user_id: user.user_id,
             nick: user.nick,
            farm_region: user.farm_region
             };

        console.log('로그인 성공! 세션 생성됨:', req.session.user);


         res.redirect('/'); 

     } else {

         console.log('로그인 실패: 비밀번호 불일치');
         return res.send('<script>alert("비밀번호가 일치하지 않습니다."); location.href="/login.html";</script>');
        }

     } catch (error) {
         console.error('DB 로그인 오류:', error);
         res.status(500).send('<script>alert("서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."); location.href="/login.html";</script>');
     }
});

// ------------------------------------------------------------------
// GET /db/logout: 로그아웃 처리
// ------------------------------------------------------------------
router.get('/logout', (req, res) => {

        if (req.session.user) {

         req.session.destroy(err => {
            if (err) {
                 console.error('세션 삭제 오류:', err);
                    return res.redirect('/'); 
            }
         console.log('로그아웃 성공: 세션 삭제 완료');

             res.redirect('/');
        });
    } else {
        
        res.redirect('/');
}
});

// ==================================================================
// ✅ 회원 정보 조회/수정 라우트 추가
// ==================================================================

// ------------------------------------------------------------------
// GET /db/user_info: 현재 로그인된 사용자 정보 조회 (update.html 로딩 시 사용)
// ------------------------------------------------------------------
router.get('/user_info', async (req, res) => {
    // 세션에서 사용자 ID 확인
    const user_id = req.session.user?.user_id;

    if (!user_id) {
        // 로그인 정보가 없는 경우
        return res.json({ 
            success: false, 
            message: "로그인 정보가 없습니다." 
        });
    }

    try {
        // DB에서 사용자 정보 조회 (비밀번호 제외)
        const sql = 'SELECT user_id, nick, farm_region FROM tb_user WHERE user_id = ?';
        const [rows] = await db.query(sql, [user_id]); 

        if (rows.length > 0) {
            res.json({
                success: true,
                user: rows[0]
            });
        } else {
            // 사용자는 로그인되었으나 DB에 없는 경우
            res.json({
                success: false,
                message: "사용자 정보를 찾을 수 없습니다."
            });
        }
    } catch (error) {
        console.error('DB 사용자 정보 조회 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: "서버 오류가 발생했습니다." 
        });
    }
});


// ------------------------------------------------------------------
// POST /db/update_info: 회원 정보 수정 처리 (본인 인증 포함)
// ------------------------------------------------------------------
router.post('/update_info', async (req, res) => {
    // 1. 세션에서 user_id 확인
    const user_id = req.session.user?.user_id;

    if (!user_id) {
        return res.status(401).json({ 
            success: false, 
            message: "로그인이 필요합니다." 
        });
    }

    // 2. 클라이언트 데이터 받기
    const { currentPw, nick, farm_region, newPw } = req.body; 

    // 3. 현재 비밀번호로 본인 인증
    const authSql = 'SELECT pwd FROM tb_user WHERE user_id = ?';
    
    try {
        const [authRows] = await db.query(authSql, [user_id]);

        if (authRows.length === 0) {
            return res.status(404).json({ 
                success: false, 
                message: "사용자 정보를 찾을 수 없습니다." 
            });
        }

        const user = authRows[0];
        // 현재 비밀번호 일치 확인 (평문 비교)
        if (currentPw !== user.pwd) { 
            return res.json({ 
                success: false, 
                message: "현재 비밀번호가 일치하지 않습니다. 다시 입력해주세요." 
            });
        }
        
        // 4. 비밀번호 일치: 이제 정보 수정 시작
        let sql = 'UPDATE tb_user SET nick = ?, farm_region = ?';
        const values = [nick, farm_region];
        let message = "회원 정보(닉네임, 지역)가 성공적으로 수정되었습니다.";

        if (newPw) {
            // 새 비밀번호가 있다면 비밀번호도 업데이트
            sql += ', pwd = ?';
            values.push(newPw);
            message = "회원 정보 및 비밀번호가 성공적으로 수정되었습니다.";
        }
        
        sql += ' WHERE user_id = ?';
        values.push(user_id);

        const [result] = await db.query(sql, values);
        
        if (result.affectedRows === 0) {
            return res.json({ 
                success: false, 
                message: "업데이트에 실패했거나 변경사항이 없습니다." 
            });
        }

        // 5. 성공 응답 전 세션 정보 갱신
        req.session.user.nick = nick;
        req.session.user.farm_region = farm_region;
        
        console.log('회원 정보 수정 및 세션 갱신 성공:', req.session.user);

        res.json({
            success: true,
            message: message
        });

    } catch (error) {
        console.error('DB 회원 정보 수정 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: "서버 오류가 발생했습니다." 
        });
    }
});


// ==================================================================
// ✅ 방제 기록 등록 라우트 추가
// ==================================================================

// ------------------------------------------------------------------
// POST /db/disinfestation_register: 방제 기록 등록 (DB 스키마 반영)
// ------------------------------------------------------------------
router.post('/disinfestation_register', async (req, res) => {
    const user_id = req.session.user?.user_id;

    if (!user_id) {
        return res.status(401).json({ 
            success: false, 
            message: "로그인이 필요합니다. 먼저 로그인해주세요." 
        });
    }

    // 클라이언트에서 받은 데이터
    const { date, pestType, chemicalName, dilutionRate, areaTreated, weather, notes } = req.body; 

    if (!date || !pestType || !chemicalName || !dilutionRate || !areaTreated || !weather) {
        return res.json({ 
            success: false, 
            message: "필수 입력 항목을 모두 입력해야 합니다." 
        });
    }
    
    // areaTreated(면적)와 weather(날씨)를 notes(disf_memo)에 합쳐서 저장합니다.
    const memo = `[면적: ${areaTreated}, 날씨: ${weather}] ${notes || ''}`;

    // 🚨 DB 컬럼 이름과 테이블 이름을 'tb_disinfestation' 스키마에 맞게 수정했습니다.
    const sql = `
        INSERT INTO tb_disinfestation 
        (user_id, pest_idx, disf_at, chemical_name, dosage, disf_memo)
        VALUES (?, ?, ?, ?, ?, ?)
    `;
    
    // pestType -> pest_idx (int), date -> disf_at (datetime), dilutionRate -> dosage (varchar/text), memo -> disf_memo
    // 가정: pestType으로 받은 값이 DB의 pest_idx 컬럼에 저장 가능한 형태(예: 숫자)라고 가정합니다.
    const values = [user_id, pestType, date, chemicalName, dilutionRate, memo];

    try {
        const [result] = await db.query(sql, values);
        
        if (result.affectedRows === 1) {
            console.log('방제 기록 DB 저장 성공:', result);
            res.json({
                success: true,
                message: "방제 기록이 성공적으로 등록되었습니다. 메인 페이지로 돌아갑니다."
            });
        } else {
            res.json({ 
                success: false, 
                message: "DB에 기록 등록 중 오류가 발생했습니다. (영향받은 행 없음)" 
            });
        }

    } catch (error) {
        console.error('DB 방제 기록 등록 오류 (SQL Error):', error.code, error.sqlMessage);
        // 에러를 콘솔에 자세히 출력하고, 클라이언트에는 DB 스키마 관련 메시지를 보냅니다.
        res.status(500).json({ 
            success: false, 
            message: `등록 실패: 서버 오류가 발생했습니다. DB 스키마를 확인하세요. (Error Code: ${error.code})` 
        });
    }
});


module.exports = router;
