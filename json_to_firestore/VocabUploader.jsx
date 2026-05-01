import React, { useState } from 'react';
import { db } from '../firebase'; 
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';

const VocabUploader = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    console.log("--- STARTING VERSION 4 UPLOAD ---");
    try {
      const data = JSON.parse(jsonInput);
      setStatus('⏳ VERSION 4: Processing...');

      for (const item of data) {
        // THE SLASH FIX
        const cleanWord = item.palabra
          .replace(/\//g, '-')    
          .replace(/\s+/g, '_')   
          .replace(/[()]/g, '')   
          .toLowerCase();

        const cleanTextbook = item.metadata.textbook.replace(/\s+/g, '_').toLowerCase();
        const docId = `${cleanTextbook}_${cleanWord}`;

        // Verify the ID in the console - if you see a '/', this code didn't run!
        console.log(`NEW ID GENERATED: ${docId}`);

        await setDoc(doc(db, "vocabulary", docId), {
          ...item,
          lastUpdated: serverTimestamp()
        });
      }

      setStatus('✅ SUCCESS: Version 4 Complete');
    } catch (error) {
      console.error("V4 ERROR:", error);
      setStatus('❌ Error: Check Console');
    }
  };

  return (
    <div className="p-10 max-w-4xl mx-auto bg-slate-900 text-white rounded-2xl shadow-2xl border-4 border-orange-500">
      <h2 className="text-2xl font-black mb-4 uppercase text-orange-500">
        🚀 VOCAB UPLOADER (V4)
      </h2>
      <p className="mb-4 text-sm text-slate-400">If this box isn't orange, you are seeing old code.</p>
      
      <textarea
        className="w-full h-96 p-4 bg-slate-800 border border-slate-700 rounded-xl font-mono text-xs text-orange-400 outline-none"
        value={jsonInput}
        onChange={(e) => setJsonInput(e.target.value)}
        placeholder="Paste JSON here..."
      />

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={handleUpload}
          className="px-8 py-3 bg-orange-600 hover:bg-orange-500 font-bold rounded-xl shadow-lg uppercase text-sm"
        >
          Push to Firestore (V4)
        </button>
        <span className="font-bold text-sm text-orange-300">{status}</span>
      </div>
    </div>
  );
};

export default VocabUploader;
