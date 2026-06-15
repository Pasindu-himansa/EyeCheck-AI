import { useState } from "react";
import ImageUpload from "./components/ImageUpload";
import ResultCard from "./components/ResultCard";

const TEST_TYPES = [{ value: "cornea_topography", label: "Cornea Topography" }];

function App() {
  const [selectedTest, setSelectedTest] = useState("cornea_topography");
  const [selectedModel, setSelectedModel] = useState("groq");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", selectedModel);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/analyze/cornea-topography",
        {
          method: "POST",
          body: formData,
        },
      );

      if (!response.ok) throw new Error("Analysis failed");

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex flex-col items-center justify-center py-10 px-4">
      <h1 className="text-3xl font-bold text-white mb-8 tracking-wide text-center">
        EyeCheck AI
      </h1>

      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        {/* Left: Input panel */}
        <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl shadow-xl p-6 flex flex-col">
          <label className="block text-sm font-medium text-white/80 mb-2">
            Select Test Type
          </label>
          <select
            value={selectedTest}
            onChange={(e) => setSelectedTest(e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-md p-2 text-white backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
          >
            {TEST_TYPES.map((test) => (
              <option
                key={test.value}
                value={test.value}
                className="text-black"
              >
                {test.label}
              </option>
            ))}
          </select>

          {/* Model toggle */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-white/80 mb-2">
              Analysis Model
            </label>
            <div className="flex rounded-md border border-white/20 overflow-hidden">
              <button
                onClick={() => setSelectedModel("groq")}
                className={`flex-1 py-2 text-sm font-medium transition ${
                  selectedModel === "groq"
                    ? "bg-cyan-500 text-white"
                    : "bg-white/5 text-white/60 hover:bg-white/10"
                }`}
              >
                Groq AI (Vision)
              </button>
              <button
                onClick={() => setSelectedModel("local")}
                className={`flex-1 py-2 text-sm font-medium transition ${
                  selectedModel === "local"
                    ? "bg-cyan-500 text-white"
                    : "bg-white/5 text-white/60 hover:bg-white/10"
                }`}
              >
                Local Model (CNN)
              </button>
            </div>
            {selectedModel === "local" && (
              <p className="mt-2 text-xs text-white/40">
                Local model expects an axial/sagittal curvature map (Sag_A type
                image).
              </p>
            )}
          </div>

          {selectedTest === "cornea_topography" && (
            <ImageUpload onAnalyze={handleAnalyze} />
          )}

          {loading && (
            <p className="mt-4 text-sm text-cyan-300 animate-pulse">
              Analyzing image...
            </p>
          )}

          {error && <p className="mt-4 text-sm text-red-400">Error: {error}</p>}
        </div>

        {/* Right: Output panel */}
        <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl shadow-xl p-6 flex items-center justify-center">
          {result ? (
            <ResultCard result={result} />
          ) : (
            <p className="text-white/50 text-sm text-center">
              Results will appear here after analysis
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
