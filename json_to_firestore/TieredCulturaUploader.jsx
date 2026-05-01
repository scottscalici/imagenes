import React, { useState } from 'react';
import { db } from '../firebase'; 
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';

const TieredCulturaUploader = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    console.log("--- STARTING TIERED READINGS UPLOAD ---");
    try {
      const data = JSON.parse(jsonInput);
      setStatus('⏳ Processing Tiered Readings...');

      for (const item of data) {
        // Create a clean ID from the topicName (e.g., "México: El Gigante" -> "mexico_el_gigante")
        const cleanName = item.topicName
          .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // Remove accents
          .replace(/[^a-zA-Z0-9 ]/g, "") // Remove punctuation
          .replace(/\s+/g, '_') // Replace spaces with underscores
          .toLowerCase();
          
        const docId = `tiered_${cleanName}`;

        console.log(`UPLOADING TIERED DOC: ${docId}`);

        // Push to a completely separate collection: "tiered_readings"
        await setDoc(doc(db, "tiered_readings", docId), {
          topicName: item.topicName,
          imageFileName: item.imageFileName,
          bundles: item.bundles || [],
          levels: {
            level_1: {
              tier: "Level 1 (English/Beginner)",
              readingText: item.levels.level_1.readingText,
              instruction: item.levels.level_1.instruction,
              questions: item.levels.level_1.questions,
              answerKey: item.levels.level_1.answerKey
            },
            level_2: {
              tier: "Level 2 (Structured Spanish)",
              readingText: item.levels.level_2.readingText,
              instruction: item.levels.level_2.instruction,
              questions: item.levels.level_2.questions,
              answerKey: item.levels.level_2.answerKey
            },
            level_3: {
              tier: "Level 3 (Natural Spanish)",
              readingText: item.levels.level_3.readingText,
              instruction: item.levels.level_3.instruction,
              questions: item.levels.level_3.questions,
              answerKey: item.levels.level_3.answerKey
            }
          },
          lastUpdated: serverTimestamp()
        });
      }

      setStatus('✅ SUCCESS: Tiered Upload Complete');
    } catch (error) {
      console.error("TIERED UPLOAD ERROR:", error);
      setStatus('❌ Error: Check Console');
    }
  };

  return (
    <div className="p-10 max-w-4xl mx-auto bg-slate-900 text-white rounded-2xl shadow-2xl border-4 border-purple-500">
      <h2 className="text-2xl font-black mb-4 uppercase text-purple-500">
        📚 TIERED READINGS UPLOADER
      </h2>
      <p className="mb-4 text-sm text-slate-400">Upload bulk JSON for Level 1, 2, and 3 cultural passages.</p>
      
      <textarea
        className="w-full h-96 p-4 bg-slate-800 border border-slate-700 rounded-xl font-mono text-xs text-purple-400 outline-none"
        value={jsonInput}
        onChange={(e) => setJsonInput(e.target.value)}
        placeholder="Paste your massive Tiered JSON here in chunks..."
      />

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={handleUpload}
          className="px-8 py-3 bg-purple-600 hover:bg-purple-500 font-bold rounded-xl shadow-lg uppercase text-sm"
        >
          Push to Firestore (Tiered)
        </button>
        <span className="font-bold text-sm text-purple-300">{status}</span>
      </div>
    </div>
  );
};

export default TieredCulturaUploader;
