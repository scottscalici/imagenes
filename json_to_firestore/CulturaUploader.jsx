import React, { useState } from 'react';
import { db } from '../firebase'; 
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';

const CulturaUploader = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    console.log("--- STARTING CULTURA UPLOAD ---");
    try {
      const data = JSON.parse(jsonInput);
      setStatus('⏳ Processing Culture Data...');

      for (const item of data) {
        // Generate a clean ID based on country and category
        const cleanCountry = item.metadata.country.replace(/\s+/g, '_').toLowerCase();
        const cleanCategory = item.metadata.category.toLowerCase();
        
        // Final ID: e.g., "culture_costa_rica_overview"
        const docId = `${cleanCategory}_${cleanCountry}`;

        console.log(`UPLOADING CULTURE DOC: ${docId}`);

        await setDoc(doc(db, "culture", docId), {
          ...item,
          lastUpdated: serverTimestamp()
        });
      }

      setStatus('✅ SUCCESS: Culture Upload Complete');
    } catch (error) {
      console.error("CULTURA ERROR:", error);
      setStatus('❌ Error: Check Console');
    }
  };

  return (
    <div className="p-10 max-w-4xl mx-auto bg-slate-900 text-white rounded-2xl shadow-2xl border-4 border-blue-500">
      <h2 className="text-2xl font-black mb-4 uppercase text-blue-500">
        🌍 CULTURA UPLOADER
      </h2>
      <p className="mb-4 text-sm text-slate-400">Pura Vida! Use this to bulk upload cultural reading units.</p>
      
      <textarea
        className="w-full h-96 p-4 bg-slate-800 border border-slate-700 rounded-xl font-mono text-xs text-blue-400 outline-none"
        value={jsonInput}
        onChange={(e) => setJsonInput(e.target.value)}
        placeholder="Paste Culture JSON here..."
      />

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={handleUpload}
          className="px-8 py-3 bg-blue-600 hover:bg-blue-500 font-bold rounded-xl shadow-lg uppercase text-sm"
        >
          Push to Firestore (Cultura)
        </button>
        <span className="font-bold text-sm text-blue-300">{status}</span>
      </div>
    </div>
  );
};

export default CulturaUploader;
