import React, { useState } from 'react';
import { db } from '../firebase'; 
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';

const DestacadoUploader = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    console.log("--- STARTING DESTACADO MASTER UPLOAD ---");
    try {
      const rawData = JSON.parse(jsonInput);
      const dataArray = Array.isArray(rawData) ? rawData : [rawData];
      
      setStatus(`⏳ Processing ${dataArray.length} highlights...`);

      for (const item of dataArray) {
        // Create a unique ID based on Day and Location
        // e.g., "dia_001_espana"
        const cleanLocation = item.location
          .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
          .replace(/[^a-zA-Z0-9]/g, '_')
          .toLowerCase();
          
        const docId = `dia_${item.dia.toString().padStart(3, '0')}_${cleanLocation}`;

        console.log(`UPLOADING DESTACADO: ${docId}`);

        await setDoc(doc(db, "destacado_diario", docId), {
          ...item,
          lastUpdated: serverTimestamp()
        });
      }

      setStatus(`✅ SUCCESS: ${dataArray.length} Highlights Synced`);
      setJsonInput(''); 
    } catch (error) {
      console.error("DESTACADO UPLOAD ERROR:", error);
      setStatus('❌ Error: Check Console');
    }
  };

  return (
    <div className="p-10 max-w-4xl mx-auto bg-slate-900 text-white rounded-2xl shadow-2xl border-4 border-blue-500">
      <h2 className="text-2xl font-black mb-4 uppercase text-blue-500">
        🌎 Destacado Diario Architect
      </h2>
      <p className="mb-4 text-sm text-slate-400">
        Populate the <code className="text-blue-300">destacado_diario</code> collection.
      </p>
      
      <textarea
        className="w-full h-96 p-4 bg-slate-800 border border-slate-700 rounded-xl font-mono text-xs text-blue-400 outline-none"
        value={jsonInput}
        onChange={(e) => setJsonInput(e.target.value)}
        placeholder='Paste Destacado JSON here...'
      />

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={handleUpload}
          className="px-8 py-3 bg-blue-600 hover:bg-blue-500 transition-all font-bold rounded-xl shadow-lg uppercase text-sm"
        >
          Push to Firestore
        </button>
        <span className="font-bold text-sm text-blue-300">{status}</span>
      </div>
    </div>
  );
};

export default DestacadoUploader;
