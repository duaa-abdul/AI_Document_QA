const fileInput =
    document.getElementById("fileInput");

const selectedFiles =
    document.getElementById("selectedFiles");

const uploadBtn =
    document.getElementById("uploadBtn");

const uploadStatus =
    document.getElementById("uploadStatus");

const askBtn =
    document.getElementById("askBtn");

const questionInput =
    document.getElementById("question");

const techniqueInput =
    document.getElementById("technique");

const answer =
    document.getElementById("answer");

const sources =
    document.getElementById("sources");

const compareBtn =
    document.getElementById("compareBtn");

const comparison =
    document.getElementById("comparison");

const testQuestions =
    document.getElementById("testQuestions");


// ==========================================
// SHOW SELECTED FILES
// ==========================================

fileInput.addEventListener(
    "change",
    function () {

        selectedFiles.innerHTML = "";

        const files =
            fileInput.files;

        for (const file of files) {

            const div =
                document.createElement("div");

            div.className =
                "file-item";

            div.textContent =
                "📄 " + file.name;

            selectedFiles.appendChild(div);
        }
    }
);


// ==========================================
// UPLOAD DOCUMENTS
// ==========================================

uploadBtn.addEventListener(
    "click",
    async function () {

        const files =
            fileInput.files;

        if (files.length === 0) {

            uploadStatus.textContent =
                "Please select at least one document.";

            return;
        }


        const formData =
            new FormData();


        for (const file of files) {

            formData.append(
                "files",
                file
            );
        }


        uploadStatus.textContent =
            "Processing documents, creating chunks and embeddings...";


        uploadBtn.disabled = true;


        try {

            const response =
                await fetch(
                    "/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Upload failed."
                );
            }


            uploadStatus.textContent =
                `✅ Success! ${data.documents} documents processed and ${data.chunks} chunks embedded into ChromaDB.`;


        }

        catch (error) {

            uploadStatus.textContent =
                "❌ Error: " +
                error.message;

        }

        finally {

            uploadBtn.disabled = false;

        }

    }
);


// ==========================================
// ASK QUESTION
// ==========================================

askBtn.addEventListener(
    "click",
    async function () {

        const question =
            questionInput.value.trim();

        const technique =
            techniqueInput.value;


        if (!question) {

            alert(
                "Please enter a question."
            );

            return;
        }


        answer.textContent =
            "Thinking...";

        sources.innerHTML =
            "";


        try {

            const response =
                await fetch(
                    "/ask",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            question:
                                question,

                            technique:
                                technique
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Something went wrong."
                );
            }


            answer.textContent =
                data.answer;


            displaySources(
                data.sources
            );

        }

        catch (error) {

            answer.textContent =
                "❌ Error: " +
                error.message;

        }

    }
);


// ==========================================
// DISPLAY SOURCES
// ==========================================

function displaySources(
    retrievedSources
) {

    sources.innerHTML = "";


    if (
        !retrievedSources ||
        retrievedSources.length === 0
    ) {

        sources.innerHTML =
            '<p class="empty">No sources found.</p>';

        return;
    }


    retrievedSources.forEach(
        (source, index) => {

            const div =
                document.createElement("div");


            div.className =
                "source-card";


            div.innerHTML = `
                <h3>
                    ${index + 1}.
                    📄
                    ${escapeHtml(source.source)}
                </h3>

                <div class="score">
                    Similarity:
                    ${source.similarity_percent}%
                </div>

                <div class="distance">
                    Distance:
                    ${source.distance}
                </div>

                <div class="source-content">
                    ${escapeHtml(source.content)}
                </div>
            `;


            sources.appendChild(div);

        }
    );
}


// ==========================================
// PROMPT COMPARISON
// ==========================================

compareBtn.addEventListener(
    "click",
    async function () {

        const question =
            questionInput.value.trim();


        if (!question) {

            alert(
                "Enter a question first."
            );

            return;
        }


        comparison.innerHTML =
            "<p>Generating answers using all three prompting techniques...</p>";


        compareBtn.disabled = true;


        try {

            const response =
                await fetch(
                    "/compare",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            question:
                                question
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Comparison failed."
                );
            }


            comparison.innerHTML = "";


            const techniques = [
                "zero-shot",
                "few-shot",
                "role-based"
            ];


            techniques.forEach(
                technique => {

                    const div =
                        document.createElement(
                            "div"
                        );


                    div.className =
                        "technique-card";


                    div.innerHTML = `
                        <h3>
                            ${formatTechnique(
                                technique
                            )}
                        </h3>

                        <p>
                            ${escapeHtml(
                                data.results[
                                    technique
                                ]
                            )}
                        </p>
                    `;


                    comparison.appendChild(
                        div
                    );

                }
            );


            // Add comparison note
            const note =
                document.createElement("div");

            note.className =
                "comparison-note";

            note.innerHTML = `
                <h3>📊 Comparison</h3>

                <p>
                    All three techniques used the
                    same retrieved document context.
                    Compare their answers based on:
                    <strong>accuracy, relevance,
                    clarity and completeness.</strong>
                </p>
            `;

            comparison.appendChild(note);

        }

        catch (error) {

            comparison.innerHTML =
                `<p>❌ Error: ${escapeHtml(
                    error.message
                )}</p>`;

        }

        finally {

            compareBtn.disabled = false;

        }

    }
);


// ==========================================
// LOAD FIVE TEST QUESTIONS
// ==========================================

async function loadTestQuestions() {

    try {

        const response =
            await fetch(
                "/test-questions"
            );

        const data =
            await response.json();


        testQuestions.innerHTML = "";


        data.questions.forEach(
            (question, index) => {

                const button =
                    document.createElement(
                        "button"
                    );


                button.className =
                    "question-btn";


                button.textContent =
                    `${index + 1}. ${question}`;


                button.addEventListener(
                    "click",
                    function () {

                        questionInput.value =
                            question;

                        questionInput.focus();

                    }
                );


                testQuestions.appendChild(
                    button
                );

            }
        );

    }

    catch (error) {

        testQuestions.innerHTML =
            "<p>Unable to load test questions.</p>";

    }
}


loadTestQuestions();


// ==========================================
// FORMAT TECHNIQUE NAME
// ==========================================

function formatTechnique(
    technique
) {

    if (technique === "zero-shot") {
        return "🎯 Zero-Shot Prompting";
    }

    if (technique === "few-shot") {
        return "📚 Few-Shot Prompting";
    }

    if (technique === "role-based") {
        return "👨‍🏫 Role-Based Prompting";
    }

    return technique;
}


// ==========================================
// ESCAPE HTML
// ==========================================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;
}