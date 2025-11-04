import { useEffect, useState } from "react";
import { getMessage } from "./api/apiClient";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getMessage().then(setData);
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "3rem" }}>
      <h1>Frontend + FastAPI</h1>
      <p>{data ? data.message : "Loading..."}</p>
    </div>
  );
}

export default App;
