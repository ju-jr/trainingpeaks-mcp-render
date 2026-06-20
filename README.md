# TrainingPeaks MCP — Deploy no Render

Wrapper SSE para rodar o [trainingpeaks-mcp](https://github.com/JamsusMaximus/trainingpeaks-mcp) como servidor remoto acessível pelo Claude.ai.

## Passo a passo

### 1. Criar repositório no GitHub

Crie um repositório novo (ex: `trainingpeaks-mcp-render`) e suba esses 3 arquivos:
- `sse_server.py`
- `requirements.txt`
- `render.yaml`

### 2. Deploy no Render

1. Acesse [render.com](https://render.com) e faça login
2. Clique em **New → Web Service**
3. Conecte seu repositório GitHub
4. O Render vai detectar o `render.yaml` automaticamente
5. Em **Environment Variables**, adicione:
   - `TP_COOKIE` → cole o valor do cookie do TrainingPeaks (o mesmo que você usou no `tp-mcp auth`)

> **Como pegar o cookie novamente:**
> 1. Acesse trainingpeaks.com logado
> 2. DevTools (F12) → Application → Cookies → trainingpeaks.com
> 3. Copie o valor do cookie `Production_tpAuth`

6. Clique em **Deploy**

### 3. Conectar no Claude.ai

Após o deploy, o Render fornecerá uma URL como:
```
https://trainingpeaks-mcp.onrender.com
```

No Claude.ai:
**Settings → Integrations → Add MCP Server**
```
URL: https://trainingpeaks-mcp.onrender.com/sse
```

## ⚠️ Segurança

Este servidor dá acesso total à sua conta TrainingPeaks. Mantenha o repositório **privado** e nunca commite o cookie diretamente no código.
