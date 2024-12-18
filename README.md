# User CURD MVC with Flask

這是一個使用 Flask 框架構建的簡單用戶管理應用程式。應用程式允許用戶創建、編輯和刪除用戶。

## 專案結構
```
│  .gitignore
│  Dockerfile
│  LICENSE
│  README.md
│  requirements.txt
│
└─src
    │  apiResponse.py
    │  app.py
    │  controllers.py
    │  models.py
    │  seeder.py
    │
    └─templates
            create.html
            edit.html
            index.html
            login.html
```

## 安裝與運行

1. 克隆此專案到本地端：
    ```bash
    git clone https://github.com/lucashsu95/user-mvc-with-flask.git
    cd user-mvc-with-flask
    ```

2. 建立並啟動虛擬環境：
    ```bash
    python -m venv .venv
    source venv/bin/activate  # Windows 使用者，請使用 `.venv\Scripts\activate`
    ```
    若要退出虛擬環境，可以在終端機中執行以下命令：
    ```sh
    deactivate  # Windows 使用者，請使用 `deactivate`
    ```

3. 安裝所需的套件：
    ```bash
    pip install -r requirements.txt
    ```

4. 運行應用程式：****
    ```bash
    python src/app.py
    ```

5. 在瀏覽器中打開 `http://127.0.0.1:5000` 來訪問應用程式。

### 使用Docker

#### 使用現成
```bash
docker run -it --rm -v ".:/app" -p 5000:5000 lucashsu95/user-mvc-with-flask:latest
```

#### 親手build
```bash
docker build -t user-mvc-with-flask .
docker run -it --rm -v ".:/app" -p 5000:5000 user-mvc-with-flask
```

## API 資料格式

| User                | 使用者                                                      |
| ------------------- | ----------------------------------------------------------- |
| id: Number          | 使用者 id，唯一值                                           |
| email: String       | 使用者的 email，唯一值                                      |
| name:String         | 使用者的暱稱                                                |
| access_token:String | 使用者的登入 token，只有在登入 API 時顯示，其餘時候不得存在 |

## API. 1 使用者登入
使用者輸入正確的帳號密碼後需回傳 access_token

**POST `/api/auth`**

**Request Body (JSON)**

```json
{
  "email": String,
  "password": String,
}
```

**Response Body**
```json
{
  "success":true,
  "data":User,
}
```

## API. 2 使用者登出
必須登入，登出後需撤銷原 access_token 的登入權限
**DELETE `/api/auth`**

**Response Body**
```json
{
  "success":true,
}
```

## API. 3 查看使用者列表
不應回傳 User 的 access_token
**GET `/api/users`**

**Response Body**
```json
{
  "success": true,
  "data": User[]
}
```
## API. 4 新增使用者

**POST `/api/users`**

**Request Body**
```json
{
  "email": String,
  "password": String,
  "name": String
}
```
**Response Body**
```json
{
  "success": true,
  "data": User
}
```
## API. 5 獲取使用者

**GET `/api/users/{user-id}`**

**Response Body**
```json
{
  "success": true,
  "data": User
}
```

<!-- 
### `/api/users/{user-id}` PUT

```json
{
  "email"?:"user11@web.tw",
  "password"?:"user11pass",
  "name"?:"user11 - t"
}
``` -->

## 錯誤訊息列表

| #   | 訊息                     | 狀態碼 | 情境                     | 適用API |
| --- | ------------------------ | ------ | ------------------------ | ------- |
| 1   | MSG_EMAIL_EXISTS         | 400    | 使用者已存在(Email 重複) | 4       |
| 2   | MSG_USER_NOT_EXISTS      | 404    | 不存在的使用者           | 5       |
| 3   | MSG_MISSING_FIELDS       | 400    | 缺少必要欄位             | 3       |
| 4   | MSG_PASSWORD_TOO_SHORT   | 400    | 密碼長度不足             | 3,6     |
| 5   | MSG_INVALID_LOGIN        | 401    | 使用者不存在、帳密有誤   | 1       |
| 6   | MSG_INVALID_ACCESS_TOKEN | 401    | 無效的 Access Token      | 2,6,7   |
| 7   | MSG_PERMISSION_DENY      | 403    | 權限不足                 | 6,7     |

## API Endpoints

| #   | URL                  | Method | Description    |
| --- | -------------------- | ------ | -------------- |
| 1   | /api/auth            | POST   | 登入           |
| 2   | /api/auth            | DELETE | 登出           |
| 3   | /api/users           | GET    | 查看使用者列表 |
| 4   | /api/users           | POST   | 新增使用者     |
| 5   | /api/users/{user-id} | GET    | 獲取使用者     |
| 6   | /api/users/{user-id} | PUT    | 更新使用者     |
| 7   | /api/users/{user-id} | DELETE | 刪除使用者     |

## 文件說明

- `src/app.py` - 應用程式的入口點，初始化數據庫並運行 `Flask` 應用程式。
- `src/controllers.py` - 定義了所有的路由和相應的處理函數。
- `src/models.py` - 定義了`User`數據庫模型。
- `src/apiResponse.py` - 回應格式
- `src/seeder.py` - 為資料庫渲染假資料
- `src/templates/` - 存放 HTML 模板文件。

## 現成路由

沒有做很多優化，可能有些問題，用API就好

- `/` - 用戶列表頁面
- `/create` - 創建新用戶頁面
- `/edit/<int:id>` - 編輯用戶頁面
- `/delete/<int:id>` - 刪除用戶功能
- `/login` - 登入
- `/logout` - 登出

## Feature
`
- [x] USER - CURD
- [x] 新增password欄位
- [x] 檢查password是否大於8個字元
- [x] 新增login、logout功能
- [x] 只能對自己修改、刪除
- [ ] 實做middleware

## Libary

- Python 3.13.0
- Flask
- flask_responses
- flask_SQLAlchemy
- flask_restful
- flask_login
- flask_cors

## 貢獻

歡迎提交問題和請求合併。如果您有任何建議或改進，請隨時提交。