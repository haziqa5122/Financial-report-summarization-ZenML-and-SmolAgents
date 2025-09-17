# Financial Report Analysis Pipeline

## Overview

This repository contains a **financial report analysis pipeline** built using **ZenML** and **SmolAgents**. The goal of this project is to process financial documents, extract key insights, and provide structured summaries, without relying on a single monolithic LLM call.

Instead, we break the task into **chained steps**:

1. **Extract**: Pull relevant data from financial reports.
2. **Summarize**: Condense the extracted information into meaningful insights.
3. **Refine**: Optimize and validate insights across multiple stages.

**ZenML** orchestrates the pipeline, ensuring reproducibility and smooth data flow, while **SmolAgents** provides lightweight, modular AI agents that handle document processing efficiently. This combination allows us to leverage **LLMOps flexibility** with **AI agent intelligence**.

---

## Setup

Before running the pipeline, you need to install and configure the required tools and dependencies. Some agents also require web search capabilities, so you will need a **SearchAPI key**.

### 1. Install ZenML

ZenML simplifies the development and deployment of ML pipelines. Ensure you are using **Python 3.9–3.12**.

```bash
pip install zenml
```

#### Logging into ZenML Pro

ZenML Pro enhances pipeline orchestration and monitoring:

1. Sign up at [ZenML Pro](https://www.zenml.io/pro).
2. Run the authentication command:

```bash
zenml login
```

3. A login window will open. Once authenticated, you’re connected to ZenML.

---

### 2. Set Up Langfuse

[Langfuse](https://www.langfuse.com) provides observability for LLM applications.

1. Sign up for an account.
2. Create an organization and invite team members (free tier supports 2 users).
3. Create a project and generate both **public** and **secret** keys.

---

### 3. Configure API Keys

Create a `.env` file in your project root with the following keys:

```env
OPENAI_API_KEY=your_openai_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
HF_TOKEN=your_huggingface_token
SEARCHAPI_API_KEY=your_searchapi_key
```

---

### 4. Set Up Your Environment with `uv` and `virtualenv`

#### Step 1: Create and Activate a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

#### Step 2: Install `uv`

```bash
pip install uv
```

#### Step 3: Install Dependencies

```bash
uv pip install -r requirements.txt
```

This ensures all packages are installed efficiently into your virtual environment.

Here’s a concise version of your dataset section with only the essential information:

---

## Dataset

The **[FINDSum dataset](https://github.com/StevenLau6/FINDSum)** is designed for financial document summarization and integrates both text and numerical table data for more informative summaries.

It contains **21,125 annual reports** from **3,794 companies**, divided into two subsets:

* **FINDSum-ROO**: Summarizes a company’s results of operations, comparing revenue and expenses.
* **FINDSum-Liquidity**: Focuses on liquidity and capital resources, assessing cash flow and financial stability.

### How to Use

The dataset includes **text files** with segmented report texts and **table files** with numerical data. To use it:

1. Load the text and table components.
2. Preprocess the data.
3. Apply summarization models.

The data is available on [Google Drive](https://drive.google.com/drive/folders/1O8HwUOp0Uxepc-SF9Oq2alxWHz03FEUE).
