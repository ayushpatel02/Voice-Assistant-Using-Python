const { useState, useEffect, useRef, useCallback } = React;

// Stable per-tab session id so the conversation has memory.
const SESSION_ID = Math.random().toString(36).slice(2);
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function Sidebar({ skills }) {
  return (
    <aside className="sidebar">
      <h2>Capabilities</h2>
      {skills.map((s) => (
        <div className="skill" key={s.name} title={s.description}>
          <div className="name">{s.name}</div>
          <div className="desc">{s.description}</div>
        </div>
      ))}
    </aside>
  );
}

function Header({ info, speak, onToggleSpeak }) {
  return (
    <header className="header">
      <div className="reactor" />
      <div className="title">J.A.R.V.I.S</div>
      <div className="status">
        <span className="dot">●</span> online · {info.tool_count ?? "…"} tools ·{" "}
        {info.provider}:{info.model}
        <button
          className="btn"
          style={{ marginLeft: 14, padding: "4px 10px" }}
          onClick={onToggleSpeak}
          title="Speak replies aloud"
        >
          {speak ? "🔊 Voice on" : "🔈 Voice off"}
        </button>
      </div>
    </header>
  );
}

function Message({ msg }) {
  return (
    <div className={`row ${msg.role}`}>
      <div className="bubble">
        <div className="who">{msg.role === "user" ? "You" : "Jarvis"}</div>
        {msg.text}
        {msg.tools && msg.tools.length > 0 && (
          <div className="trace">
            {msg.tools.map((t, i) => (
              <span className="chip" key={i}>🔧 {t}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  const [info, setInfo] = useState({});
  const [skills, setSkills] = useState([]);
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Good day, Boss. Jarvis online. How may I help?" },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [listening, setListening] = useState(false);
  const [speak, setSpeak] = useState(false);

  const wsRef = useRef(null);
  const chatEndRef = useRef(null);
  const speakRef = useRef(false);
  speakRef.current = speak;

  // Load metadata + skills.
  useEffect(() => {
    fetch("/api/info").then((r) => r.json()).then(setInfo).catch(() => {});
    fetch("/api/skills").then((r) => r.json()).then(setSkills).catch(() => {});
  }, []);

  const speakText = useCallback((text) => {
    if (!speakRef.current || !window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.0;
    window.speechSynthesis.speak(u);
  }, []);

  // WebSocket chat channel.
  useEffect(() => {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/ws`);
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data);
      if (data.type === "status") {
        setThinking(true);
      } else if (data.type === "reply") {
        setThinking(false);
        setMessages((m) => [...m, { role: "assistant", text: data.reply, tools: data.tools_used }]);
        speakText(data.reply);
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, [speakText]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  const send = useCallback((text) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    setMessages((m) => [...m, { role: "user", text: trimmed }]);
    setInput("");
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      setThinking(true);
      ws.send(JSON.stringify({ message: trimmed, session_id: SESSION_ID }));
    } else {
      // Fallback to REST if the socket isn't ready.
      setThinking(true);
      fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, session_id: SESSION_ID }),
      })
        .then((r) => r.json())
        .then((data) => {
          setThinking(false);
          setMessages((m) => [...m, { role: "assistant", text: data.reply, tools: data.tools_used }]);
          speakText(data.reply);
        });
    }
  }, [speakText]);

  const toggleMic = useCallback(() => {
    if (!SpeechRecognition) {
      alert("This browser doesn't support speech recognition. Try Chrome.");
      return;
    }
    const recog = new SpeechRecognition();
    recog.lang = "en-IN";
    recog.interimResults = false;
    setListening(true);
    recog.onresult = (e) => {
      const text = e.results[0][0].transcript;
      send(text);
    };
    recog.onend = () => setListening(false);
    recog.onerror = () => setListening(false);
    recog.start();
  }, [send]);

  return (
    <div className="app">
      <Sidebar skills={skills} />
      <div className="main">
        <Header info={info} speak={speak} onToggleSpeak={() => setSpeak((s) => !s)} />
        <div className="chat">
          {messages.map((m, i) => (
            <Message msg={m} key={i} />
          ))}
          {thinking && (
            <div className="row assistant">
              <div className="bubble">
                <div className="thinking"><span /><span /><span /></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <div className="composer">
          <button
            className={`btn mic ${listening ? "listening" : ""}`}
            onClick={toggleMic}
            title="Speak"
          >
            🎙
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
            placeholder="Type a message, or tap the mic…"
            autoFocus
          />
          <button className="btn" onClick={() => send(input)}>Send ➤</button>
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
