import { useRef, useState } from "react";

export function UploadZone({ label, subtext, file, onFile }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const selectFile = (nextFile) => {
    if (nextFile) onFile(nextFile);
  };

  return (
    <label
      className={`upload-zone ${dragging ? "is-dragging" : ""} ${file ? "is-ready" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        selectFile(event.dataTransfer.files?.[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.md,.pdf"
        onChange={(event) => selectFile(event.target.files?.[0])}
      />
      <span>
        <span className="upload-symbol">{file ? "OK" : "DOC"}</span>
        <strong>{label}</strong>
        <span>{file ? file.name : subtext}</span>
      </span>
    </label>
  );
}
