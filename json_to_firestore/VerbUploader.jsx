import React, { useState } from 'react';
import { db } from '../firebase'; 
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';

const VerbUploader = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    console.log("--- STARTING VERB MASTER UPLOAD ---");
    try {
      // Parse the input. Wrapped in an array check so you can paste one verb or a list.
      const rawData = JSON.parse(jsonInput);
      const dataArray = Array.isArray(rawData) ? rawData : [rawData];
      
      setStatus(`⏳ Processing ${dataArray.length} verbs...`);

      for (const verb of dataArray) {
        if (!verb.palabra) {
            console.warn("Skipping item: No 'palabra' field found.");
            continue;
        }

        // THE SLASH & SPACE FIX
        // Ensures verbs like "reír/reírse" become "reir-reirse" for safe Firestore IDs
        const docId = verb.palabra
          .replace(/\//g, '-')    
          .replace(/\s+/g, '_')   
          .replace(/[()]/g, '')   
          .toLowerCase();

        console.log(`UPLOADING VERB: ${docId}`);

        // Uploading to the "verbs" collection
        await setDoc(doc(db, "verbs", docId), {
          ...verb,
          lastUpdated: serverTimestamp()
        });
      }

      setStatus(`✅ SUCCESS: ${dataArray.length} Verbs Synced`);
      setJsonInput(''); // Clear input on success
    } catch (error) {
      console.error("VERB UPLOAD ERROR:", error);
      setStatus('❌ Error: Check Console');
    }
  };

  return (
    <div className="p-10 max-w-4xl mx-auto bg-slate-900 text-white rounded-2xl shadow-2xl border-4 border-orange-500">
      <h2 className="text-2xl font-black mb-4 uppercase text-orange-500">
        ⚔️ Master Verb Architect Uploader
      </h2>
      <p className="mb-4 text-sm text-slate-400">
        Paste your high-fidelity JSON objects below to sync them to the <code className="text-orange-300">verbs</code> collection.
      </p>
      
      <textarea
        className="w-full h-96 p-4 bg-slate-800 border border-slate-700 rounded-xl font-mono text-xs text-orange-400 outline-none focus:border-orange-500 transition-colors"
        value={jsonInput}
        onChange={(e) => setJsonInput(e.target.value)}
        placeholder='[ { "palabra": "tener", ... } ]'
      />

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={handleUpload}
          className="px-8 py-3 bg-orange-600 hover:bg-orange-500 active:scale-95 transition-all font-bold rounded-xl shadow-lg uppercase text-sm"
        >
          Push to Firestore
        </button>
        <span className="font-bold text-sm text-orange-300">{status}</span>
      </div>
    </div>
  );
};

export default VerbUploader;
