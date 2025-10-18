import { useState } from "react";

export default function Home() {
  const [sankalpa, setSankalpa] = useState("");
  const [question, setQuestion] = useState("");
  const [resp, setResp] = useState<string>("");

  const submitSankalpa = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await fetch("http://localhost:8000/sankalpa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: sankalpa, context: "web-form" }),
    });
    const data = await r.json();
    alert(`Sankalpa created: ${data.id}`);
    setSankalpa("");
  };

  const ask = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await fetch("http://localhost:8000/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: question }),
    });
    const data = await r.json(); // { agent, data: { ok, echo: { prompt } } }
    setResp(JSON.stringify(data.data, null, 2));
  };

  return (
    <main style={{ padding: 24, maxWidth: 800, margin: "0 auto", fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: 24, marginBottom: 16 }}>Sacred QA Studio</h1>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Create Sankalpa</h2>
        <form onSubmit={submitSankalpa} style={{ display: "flex", gap: 8 }}>
          <input
            value={sankalpa}
            onChange={(e) => setSankalpa(e.target.value)}
            placeholder="Your sankalpa intention..."
            style={{ flex: 1, padding: 8, border: "1px solid #ccc" }}
            required
          />
          <button type="submit" style={{ padding: "8px 12px", background: "#2563eb", color: "white", border: 0 }}>
            Set Sankalpa
          </button>
        </form>
      </section>

      <section>
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Ask a Question</h2>
        <form onSubmit={ask} style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Your question..."
            style={{ flex: 1, padding: 8, border: "1px solid #ccc" }}
            required
          />
          <button type="submit" style={{ padding: "8px 12px", background: "#16a34a", color: "white", border: 0 }}>
            Ask
          </button>
        </form>
        {resp && (
          <pre style={{ background: "#f3f4f6", padding: 12, borderRadius: 6, whiteSpace: "pre-wrap" }}>{resp}</pre>
        )}
      </section>
    </main>
  );
}
