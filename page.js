 document.getElementById("analyzeButton").addEventListener("click", () => {
  const input = document.getElementById("videoUrlInput").value;

  fetch("http://127.0.0.1:5000/get_comments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ videoUrl: input })
  })
    .then(response => {
      if (!response.ok) throw new Error("Server error");
      return response.json();
    })
    .then(data => {
      if (data.error) {
        alert("Error: " + data.error);
        return;
      }

      document.getElementById("totalComments").innerText = `Total Comments: ${data.total_comments}`;

      document.getElementById("clearButton").addEventListener("click", () => {
  document.getElementById("videoUrlInput").value = "";
  document.getElementById("positivePercentage").innerText = "";
  document.getElementById("neutralPercentage").innerText = "";
  document.getElementById("negativePercentage").innerText = "";
  document.getElementById("totalComments").innerText = "";
  document.querySelector("#positiveComments ul").innerHTML = "";
  document.querySelector("#neutralComments ul").innerHTML = "";
  document.querySelector("#negativeComments ul").innerHTML = "";
});

      const posList = document.querySelector("#positiveComments ul");
      const neuList = document.querySelector("#neutralComments ul");
      const negList = document.querySelector("#negativeComments ul");

      posList.innerHTML = "";
      neuList.innerHTML = "";
      negList.innerHTML = "";

      data.sentiment_results.forEach(entry => {
        const li = document.createElement("li");
        li.textContent = entry.comment;
        if (entry.sentiment === "POSITIVE") posList.appendChild(li);
        else if (entry.sentiment === "NEUTRAL") neuList.appendChild(li);
        else negList.appendChild(li);
      });

      // ✅ Now insert percentages after comments are loaded
      document.getElementById("positivePercentage").innerText = 
        `Positive: ${data.sentiment_percentages.POSITIVE} (${data.sentiment_percentages.POSITIVE_PERCENT.toFixed(2)}%)`;

      document.getElementById("neutralPercentage").innerText = 
        `Neutral: ${data.sentiment_percentages.NEUTRAL} (${data.sentiment_percentages.NEUTRAL_PERCENT.toFixed(2)}%)`;

      document.getElementById("negativePercentage").innerText = 
        `Negative: ${data.sentiment_percentages.NEGATIVE} (${data.sentiment_percentages.NEGATIVE_PERCENT.toFixed(2)}%)`;
    })
    .catch(error => {
      console.error("Error:", error);
      alert("Something went wrong. Please check your backend or internet connection.");
    });
});
 