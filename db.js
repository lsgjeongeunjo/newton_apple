// config/db.js

// 🚨🚨🚨 'mysql2/promise'를 require해야 await db.query()가 작동합니다. 🚨🚨🚨
const mysql = require('mysql2/promise');

const db = mysql.createPool({
    host: "project-db-campus.smhrd.com",
    port: 3307,
    user: "campus_25IS_health1_p2_3",
    password: "smhrd3",
    database: "campus_25IS_health1_p2_3"
});

// 연결 테스트 (Promise 방식으로 변경)
db.getConnection()
    .then(connection => {
        console.log("db connection success (Promise enabled)");
        connection.release(); // 연결 사용 후 반환
    })
    .catch(err => {
        // 연결 풀 생성 시 문제가 생기면 발생합니다.
        console.error(`DB connection pool failed: ${err.message}`); 
        process.exit(1);
    });

module.exports = db;
