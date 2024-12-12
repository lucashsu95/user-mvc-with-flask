# User CURD MVC with Flask

這是一個使用 Flask 框架構建的簡單用戶管理應用程式。應用程式允許用戶創建、編輯和刪除用戶。

## 專案結構
```
│  .gitignore
│  apiResponse.py
│  app.py
│  controllers.py
│  models.py
│  README.md
│  requirements.txt
│  seeder.py
│
└─templates
        create.html
        edit.html
        index.html
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

3. 安裝所需的套件：
    ```bash
    pip install -r requirements.txt
    ```

4. 運行應用程式：****
    ```bash
    python app.py
    ```

5. 在瀏覽器中打開 `http://127.0.0.1:5000` 來訪問應用程式。


## 路由

- `/` - 用戶列表頁面
- `/create` - 創建新用戶頁面
- `/edit/<int:id>` - 編輯用戶頁面
- `/delete/<int:id>` - 刪除用戶功能

## API

1. `/api/users` GET
2. `/api/users` POST
3. `/api/users/{user-id}` GET
4. `/api/users/{user-id}` PUT
5. `/api/users/{user-id}` DELETE


### `/api/users` POST

```json
{
  "email":"user11@web.tw",
  "name":"user11"
}
```

### `/api/users` PUT

```json
{
  "email?":"user11@web.tw",
  "name?":"user11 - t"
}
```

## 文件說明

- `app.py` - 應用程式的入口點，初始化數據庫並運行 `Flask` 應用程式。
- `controllers.py` - 定義了所有的路由和相應的處理函數。
- `models.py` - 定義了`User`數據庫模型。
- `templates/` - 存放 HTML 模板文件。
- `ApiResponse.py` - 回應格式
- `seeder.py` - 為資料庫渲染假資料

## Feature
`
- [x] USER - CURD
- [ ] 新增password欄位
- [ ] 新增login、logout功能
- [ ] 實戶middleware

## Libary

- Python 3.13.0
- Flask
- flask_responses
- flask_restful

## 貢獻

歡迎提交問題和請求合併。如果您有任何建議或改進，請隨時提交。