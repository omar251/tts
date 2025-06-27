# Plan: Display Full Text with Focused Highlighting in TTS Webpage

**Goal:** Modify the webpage to display the entire input text during audio playback, with the currently playing section highlighted and scrolled into view.

**Key Changes:**

1.  **Global Text Management:** Store the complete input text and process it once into a global structure that allows for word-by-word referencing across the entire document.
2.  **Unified Text Display:** Instead of replacing content with each paragraph, a dedicated area will display the *entire* input text from the start.
3.  **Enhanced Highlighting Logic:** The word highlighting mechanism will be updated to work across the full text, identifying paragraphs and individual words to highlight the current playing segment and ensure it's visible.

**Detailed Steps:**

1.  **Rename Display Element:**
    *   Rename the existing `<div id="current-paragraph">` (line 306) in `static/index.html` to `<div id="full-text-input-display">`.
    *   Update the corresponding CSS rules and JavaScript variable names (`currentParagraphDiv` to `fullTextInputDisplay`).

2.  **Prepare Full Text for Highlighting:**
    *   Create a new JavaScript function, `prepareFullTextForHighlighting(fullText)`.
    *   This function will take the entire text from the input area (`textInput.value`).
    *   It will split the text into paragraphs and then each paragraph into individual words.
    *   Each word will be wrapped in a `<span>` tag with a unique `data-global-word-index` attribute. This entire structured HTML will then be inserted into the `fullTextInputDisplay` element.

3.  **Update Stream Initiation:**
    *   When the "Stream Audio" button is clicked:
        *   The `prepareFullTextForHighlighting()` function will be called *before* the WebSocket stream request is sent, populating the `fullTextInputDisplay` with the entire text.
        *   Ensure the `fullTextInputDisplay` element is visible within the playback view.

4.  **Refine Word Highlighting Functions:**
    *   **`displayParagraphWithWords` (and related functions):** These will be significantly modified or replaced. The `fullTextInputDisplay` will be rendered once.
    *   **`highlightCurrentWord`:** This function will be adapted to accept a `globalWordIndex`. It will apply the visual highlighting (`word-highlight`, `pulse`) to the `<span>` element corresponding to this index within the `fullTextInputDisplay`. It will also manage scrolling to keep the highlighted word in view.
    *   **`startWordHighlighting`:** This function will be enhanced to:
        *   Identify the start and end global word indices for the `data.text` (paragraph) received from the server.
        *   Apply a distinct highlight (e.g., a new CSS class like `current-chunk-highlight`) to all words belonging to the current audio chunk.
        *   Then, it will use the word-by-word highlighting (`word-highlight`, `pulse`) within that specific chunk, advancing the `globalWordIndex` as audio plays.
        *   The `scrollIntoView` logic will prioritize keeping the *current chunk* visible, and then the *current word* within that chunk.

5.  **Adjust Audio Playback Logic:**
    *   In the `playNextAudio` function, when an `audio_url` chunk is processed:
        *   Instead of just displaying the `audioChunk.text` in isolation, we will use it to determine the `startGlobalIndex` and `endGlobalIndex` within the full text.
        *   These global indices will be passed to the refined `startWordHighlighting` function to manage highlighting for the entire document.
    *   The `onended` and `onerror` event handlers for the audio player will be updated to correctly advance the highlighting to the next chunk in the full text.

6.  **Cleanup and Reset:**
    *   The `stopWordHighlighting` and `resetWordHighlighting` functions will be updated to correctly clear all highlighting from the `fullTextInputDisplay` and reset the global word index.

**Visual Representation of the Workflow:**

```mermaid
graph TD
    A[User enters text and clicks Stream Audio] --> B[JS: Get Full Input Text];
    B --> C[JS: Prepare Full Text for Highlighting];
    C --> D[HTML: Render Full Text in Display Area];
    D --> E[JS: Send Stream Request to Server];
    E --> F{WS: Receive audio_url chunk};
    F -- data.text, data.url --> G[JS: Add Chunk to Audio Queue];
    G --> H{JS: Is Audio Player Idle?};
    H -- Yes --> I[JS: Play Next Audio Chunk];
    I --> J[JS: Load Audio URL];
    J --> K[JS: Find Global Word Indices for Chunk Text];
    K --> L[JS: Start Highlighting Current Chunk];
    L --> M[JS: Highlight Word-by-Word within Chunk];
    M --> N{Audio Chunk Ends};
    N -- Yes --> O[JS: Stop Chunk Highlighting];
    O --> P[JS: Play Next Audio Chunk (from G)];
    H -- No --> Q[JS: Wait for Current Audio to End];
    F -- complete/error --> R[JS: Mark Stream Processing Complete];