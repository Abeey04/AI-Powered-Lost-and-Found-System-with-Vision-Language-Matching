# AI-Powered Lost and Found Matching System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Optional: Choose a license -->

An intelligent system leveraging Deep Learning (BLIP and BERT) to automate the process of matching lost items with found ones through image captioning and semantic text comparison.

## Table of Contents

*   [Introduction](#introduction)
*   [Problem Statement](#problem-statement)
*   [Key Features](#key-features)
*   [How It Works](#how-it-works)

## Introduction

Losing personal belongings is stressful, and traditional lost-and-found systems are often inefficient due to manual processes. This project implements a cutting-edge, AI-powered solution that uses advanced Deep Learning models (**BLIP** for image captioning and **BERT** for text understanding) to automatically match lost items reported by users with found items logged into the system, streamlining the recovery process.

## Problem Statement

Existing lost-and-found methods suffer from:

*   **Manual Data Entry:** Slow, laborious, and prone to error.
*   **Inefficient Searching:** Relies on manual searching or basic keyword matching, often failing with vague descriptions.
*   **Lack of Real-Time Updates:** Delays in processing and notification.
*   **Scalability Issues:** Difficult to manage large volumes or across different locations.

This project addresses these issues by automating the visual and textual processing needed for matching.

## Key Features

*   **Automated Image Captioning:** Uses the **BLIP** model to generate detailed, descriptive captions (colour, shape, features) from uploaded images of found items.
*   **Semantic Text Matching:** Employs **BERT** to understand the meaning (semantic embeddings) of user-submitted descriptions of lost items.
*   **Intelligent Matching:** Compares the semantic meaning of image captions and text descriptions using **cosine similarity** to identify potential matches accurately.
*   **User-Friendly Interface:** A simple web application (built with *Streamlit/Flask/Django* - specify which one) for users to easily report lost items or upload found items.
*   **Real-Time Notifications:** Automatically alerts users (e.g., via email/SMS placeholders) when a probable match is found.

## How It Works

1.  **Found Item Upload:** A user uploads an image of an item they found.
2.  **Image Captioning (BLIP):** The system uses a fine-tuned BLIP model to generate a textual description (caption) of the item in the image.
3.  **Lost Item Report:** A user describes an item they lost via a text form.
4.  **Text Embedding (BERT):** Both the BLIP-generated caption and the user's description are processed by a fine-tuned BERT model to generate semantic vector embeddings.
5.  **Similarity Calculation:** The system calculates the **cosine similarity** between the embedding of the found item's caption and the embedding of the lost item's description.
6.  **Matching & Notification:** If the similarity score exceeds a predefined threshold (e.g., 0.6), the system flags it as a potential match and notifies the relevant users.

*(Based on Figure 1 - Workflow Diagram)*

```mermaid
graph LR
    A[User Uploads Found Item Image] --> B{BLIP Model};
    B -- Generates Caption --> C[Found Item Caption];
    D[User Reports Lost Item Text] --> E{BERT Model};
    E -- Generates Embedding --> F[Lost Item Embedding];
    C -- Processed by BERT --> G[Found Item Caption Embedding];
    G & F --> H{Cosine Similarity Check};
    H -- Score > Threshold --> I[Match Found!];
    I --> J[Notify Users];
    A --> K[(Store Image & Metadata)];
    C --> K;
    D --> L[(Store Description & Contact)];
    F --> L;
    K & L --> M[Database];
    H -- Score <= Threshold --> N[No Match];

    style B fill:#f9f,stroke:#333,stroke-width:2px;
    style E fill:#f9f,stroke:#333,stroke-width:2px;
    style H fill:#ccf,stroke:#333,stroke-width:2px;
    style M fill:#ddd,stroke:#333,stroke-width:1px;

