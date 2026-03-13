import { useState, useRef } from "react";

export default function Doctor() {

  const [transcript, setTranscript] = useState([]);
  const [isRecording, setIsRecording] = useState(false); // false, 'patient', 'doctor'
  const [report, setReport] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const recognitionRef = useRef(null);

  function startListening(role) {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
      
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    // Set language based on role
    recognition.lang = role === "patient" ? "hi-IN" : "en-IN";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = async function(event) {
      const result = event.results[event.results.length - 1];
      if (!result.isFinal) return;
      const speech = result[0].transcript;

      // Optimistically add to transcript
      setTranscript(prev => [...prev, { role, original: speech, translated: "Translating..." }]);

      try {
        const source_lang = role === "patient" ? "hi-IN" : "en-IN";
        const target_lang = role === "patient" ? "en-IN" : "hi-IN";

        const res = await fetch("http://localhost:8000/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: speech,
            source_lang,
            target_lang
          })
        });

        const data = await res.json();

        setTranscript(prev => {
          const newTranscript = [...prev];
          for (let i = newTranscript.length - 1; i >= 0; i--) {
            if (newTranscript[i].role === role && newTranscript[i].original === speech) {
              newTranscript[i].translated = data.translated_text || "Error";
              break;
            }
          }
          return newTranscript;
        });

      } catch (err) {
        console.log("Translation error", err);
      }
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setIsRecording(false);
    };

    recognition.start();
    setIsRecording(role);
  }

  function stopListening() {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  }

  async function generateReport() {
    setIsGenerating(true);
    
    const lines = transcript.map(t => {
      if (t.role === 'patient') {
        return `Patient: ${t.translated} (Original Hindi: ${t.original})`;
      } else {
        return `Doctor: ${t.original} (Translated to Hindi: ${t.translated})`;
      }
    });
    
    const combinedText = lines.join("\n");

    try {
      const res = await fetch("http://localhost:8000/sanitize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: "PAT-001",
          transcript: combinedText
        })
      });
      const data = await res.json();
      setReport(data);
    } catch (err) {
      console.error("Report generation error", err);
    }
    setIsGenerating(false);
  }

  return (
    <div style={{padding:"40px", fontFamily: "sans-serif"}}>
      <h1>Doctor Consultation Dashboard</h1>

      <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "20px" }}>
        <button 
          onClick={() => startListening("patient")} 
          disabled={isRecording}
          style={{ padding: "10px 20px", backgroundColor: isRecording ? "#ccc" : "#2196F3", color: "white", border: "none", borderRadius: "5px", cursor: isRecording ? "not-allowed" : "pointer", fontSize: "16px" }}
        >
          🎤 Patient Speaks (Hindi)
        </button>
        <button 
          onClick={() => startListening("doctor")} 
          disabled={isRecording}
          style={{ padding: "10px 20px", backgroundColor: isRecording ? "#ccc" : "#4CAF50", color: "white", border: "none", borderRadius: "5px", cursor: isRecording ? "not-allowed" : "pointer", fontSize: "16px" }}
        >
          🎤 Doctor Speaks (English)
        </button>
        <button 
          onClick={stopListening} 
          disabled={!isRecording}
          style={{ padding: "10px 20px", backgroundColor: !isRecording ? "#ccc" : "#f44336", color: "white", border: "none", borderRadius: "5px", cursor: !isRecording ? "not-allowed" : "pointer", fontSize: "16px" }}
        >
          ⏹ Stop Recording
        </button>
        {isRecording && <span style={{ color: "red", fontWeight: "bold", animation: "blink 1s infinite" }}>Recording {isRecording}...</span>}
      </div>

      <h3>Live Transcript</h3>
      <div style={{ border:"1px solid gray", padding:"10px", minHeight:"150px", marginBottom: "20px", backgroundColor: "#f9f9f9", borderRadius: "5px" }}>
        {transcript.map((t, index) => (
          <div key={index} style={{ marginBottom: "10px", padding: "10px", backgroundColor: t.role === 'patient' ? "#e3f2fd" : "#e8f5e9", borderRadius: "5px" }}>
            <strong>{t.role === 'patient' ? "Patient (Hindi): " : "Doctor (English): "}</strong>
            <p style={{ margin: "5px 0" }}>{t.original}</p>
            <p style={{ margin: "0", color: "#666", fontStyle: "italic" }}>Translation: {t.translated}</p>
          </div>
        ))}
        {transcript.length === 0 && <p style={{ color: "gray" }}>No conversation yet.</p>}
      </div>

      <button 
        onClick={generateReport}
        disabled={isGenerating || transcript.length === 0}
        style={{ padding: "10px 20px", backgroundColor: "#FF9800", color: "white", border: "none", borderRadius: "5px", cursor: (isGenerating || transcript.length === 0) ? "not-allowed" : "pointer", fontSize: "16px", marginBottom: "20px" }}
      >
        {isGenerating ? "Generating..." : "📝 Generate Report"}
      </button>

      {report && (
        <div style={{ border:"2px solid #FF9800", padding:"15px", backgroundColor: "#fff3e0", borderRadius: "5px", marginTop: "20px" }}>
          <h2 style={{ marginTop: 0 }}>Clinical Generated Summary</h2>
          <p><strong>Diagnosis:</strong> {report.diagnosis}</p>
          
          {report.symptoms && report.symptoms.length > 0 && (
            <p><strong>Symptoms:</strong> {report.symptoms.join(", ")}</p>
          )}
          
          {report.prescription && report.prescription.length > 0 && (
            <>
              <h4>Prescription</h4>
              <ul>
                {report.prescription.map((p, i) => (
                  <li key={i}>{p.medication} - {p.dosage} ({p.duration || 'As directed'})</li>
                ))}
              </ul>
            </>
          )}
          
          {report.tests && report.tests.length > 0 && (
            <>
              <h4>Tests Recommended</h4>
              <ul>
                {report.tests.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </>
          )}

          {report.followup && (
            <p><strong>Follow-up:</strong> {report.followup}</p>
          )}
        </div>
      )}

    </div>
  );
}