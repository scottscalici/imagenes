import React, { useState } from 'react';
import { db } from '../firebase'; 
import { doc, setDoc } from 'firebase/firestore';


const MusicUploader = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    try {
      const data = JSON.parse(jsonInput);
      setStatus('Uploading...');

      for (const item of data) {
        // Use the 'id' field as the Firestore Document ID
        await setDoc(doc(db, "musica", item.id), item);
        console.log(`Uploaded: ${item.titulo}`);
      }

      setStatus('✅ All songs uploaded successfully!');
    } catch (error) {
      console.error("Upload error:", error);
      setStatus('❌ Error: Check console or JSON format.');
    }
  };

  return (
    <div className="p-10 max-w-4xl mx-auto bg-slate-900 text-white rounded-2xl shadow-2xl">
      <h2 className="text-2xl font-black mb-4 uppercase tracking-tighter">🎵 Musica Bulk Uploader</h2>
      <p className="text-slate-400 text-sm mb-6">Paste your JSON array below to populate the 'musica' collection.</p>
      
      <textarea
        className="w-full h-96 p-4 bg-slate-800 border border-slate-700 rounded-xl font-mono text-xs text-emerald-400 outline-none focus:ring-2 focus:ring-emerald-500"
        value={jsonInput}
        onChange={(e) => setJsonInput(e.target.value)}
        placeholder="Paste JSON here..."
      />

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={handleUpload}
          className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 font-bold rounded-xl transition-all shadow-lg uppercase text-sm tracking-widest"
        >
          Push to Firestore
        </button>
        <span className="font-bold text-sm">{status}</span>
      </div>
    </div>
  );
};

export default MusicUploader;
