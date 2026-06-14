import { useState } from "react";
import { UploadCloud } from "lucide-react";

function ImageUpload({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    }
  };

  return (
    <div className="mt-6 border-t border-white/20 pt-4">
      <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-white/30 rounded-xl cursor-pointer bg-white/5 hover:bg-white/10 transition">
        <UploadCloud className="text-white/60 mb-2" size={28} />
        <span className="text-sm text-white/60">
          {file ? file.name : "Click to upload topography image"}
        </span>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </label>

      {preview && (
        <img
          src={preview}
          alt="Preview"
          className="w-full max-h-64 object-contain rounded-md border border-white/20 mt-4"
        />
      )}

      <button
        onClick={() => onAnalyze(file)}
        disabled={!file}
        className="w-full mt-4 bg-cyan-500 text-white py-2 rounded-md font-medium hover:bg-cyan-400 transition disabled:bg-white/10 disabled:text-white/30"
      >
        Analyze
      </button>
    </div>
  );
}

export default ImageUpload;
