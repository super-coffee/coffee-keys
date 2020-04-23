# Coffee-Keys 开发人员手册

## 一些约定
### `database.py`
- 对外 return 时，必须以 `return <boolean>, <message>` 的格式返回  
    ``` python
    m = 'Error: unable to fetch data'
    print(m)
    return False, m
    ```  
    ``` python
    m = 'Added'
    print(m)
    return True, m
    ```
    其中，`False` 表示操作失败，`True` 表示操作成功
### `coffee-keys.py`
- 由于需要进行反向代理，路由 URL 必须以 `/api` 开头
- 除特殊情况外，向前端 `return` **数据**时，需要以以下格式
    ```python
    {'status': boolean, 'data': str}
    ```
    `status` 在操作成功时为 `True`，失败时为 `False`；`data` 在操作成功时为「需要返回的数据」，失败时为「错误原因」。  
    前端实际接收到的将为 JSON 格式