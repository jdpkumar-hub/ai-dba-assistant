"use client";

import { supabase } from "../lib/supabase";

export default function Home() {

 const loginWithGoogle = async () => {
  await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: window.location.origin + "/dashboard"
    }
  });
};


  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>AI DBA Assistant</h1>

      <button
        onClick={loginWithGoogle}
        style={{
          padding: "12px 20px",
          borderRadius: "8px",
          border: "1px solid #ddd",
          cursor: "pointer"
        }}
      >
        🔵 Continue with Google
      </button>
    </div>
  );
}