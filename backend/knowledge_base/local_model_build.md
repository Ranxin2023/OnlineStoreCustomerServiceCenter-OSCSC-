# AI客服开发路线
## 第一层：Intent Router

## 第二层：Semantic Search
## 第三层：LLM fallback
## 如果你真的想做自己的 LM
### Step1
#### 收集客服对话数据
```
Buyer: where is my order
Seller: please check tracking number
```
### Step2
#### 训练一个小 transformer
### Step3
#### 做 Instruction tuning
```
<user>
where is my order

<assistant>
Please check your tracking number
```
## 五、但这里有一个现实问题
### 这种数据量：训练 LM 是 完全不够的。
### 所以你必须：
```
收集大量历史客服聊天
```
## 你现在项目最强的升级路线
```
Buyer message
        ↓
Embedding
        ↓
Intent Matching
        ↓
Template Answer
        ↓
LLM fallback
```
## 未来如果你数据很多
### 再升级：
```
Fine-tune LLM
```
### 微调成：
```
AliExpress Customer Service Model
```

### 你现在代码升级只需要三步
#### Step1
- 把 intent keywords 变成 key embedding
#### Step2
- query 做 embedding
#### Step3
- 算相似度

### 最终结构
```
buyer message
        ↓
embedding
        ↓
attention(query, intent_keys)
        ↓
best intent
        ↓
intent_answers
        ↓
reply
```
### 一个更高级的版本
#### 你可以做 intent embedding center：
#### 例如：
```
shipping_time vector
refund vector
tracking vector
```
#### Then
```
query → embedding
↓
cosine(query, intent_vector)
↓
max
```