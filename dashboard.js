async function loadDashboard() {

    const statsResponse =
        await fetch("/api/statistics");

    const stats =
        await statsResponse.json();

    document.getElementById("total").textContent =
        stats.total;

    document.getElementById("highRisk").textContent =
        stats.high_risk;

    document.getElementById("average").textContent =
        stats.average + "%";


    const topicsResponse =
        await fetch("/api/topics");

    const topics =
        await topicsResponse.json();

    const container =
        document.getElementById("topics");

    container.innerHTML = "";

    if (topics.length === 0) {

        container.innerHTML =
            "<p>No topics added yet.</p>";

        return;
    }

    topics.forEach(item => {

        const card =
            document.createElement("div");

        card.className = "topic-card";

        card.innerHTML = `
            <div>
                <h3>${item.topic}</h3>
                <p>${item.subject}</p>
            </div>

            <div class="risk">
                ${item.risk}%
                <small>${item.risk_level}</small>
            </div>
        `;

        container.appendChild(card);

    });
}


document
    .getElementById("topicForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const data = {

            topic:
                document.getElementById("topic").value,

            subject:
                document.getElementById("subject").value,

            difficulty:
                document.getElementById("difficulty").value,

            quiz_score:
                document.getElementById("quiz_score").value,

            days_since_study:
                document.getElementById("days_since_study").value,

            revisions:
                document.getElementById("revisions").value
        };


        const response =
            await fetch("/api/topics", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(data)
            });


        const result =
            await response.json();


        if (result.success) {

            document.getElementById(
                "prediction"
            ).innerHTML = `

                <div class="prediction">

                    🧠 Forgetting Risk:

                    <strong>
                        ${result.risk}%
                    </strong>

                    <br>

                    Level:
                    ${result.risk_level}

                </div>

            `;

            this.reset();

            loadDashboard();

        }

    });


loadDashboard();