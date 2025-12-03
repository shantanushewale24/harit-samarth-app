import Navbar from "@/components/Navbar";
import SensorMonitoring from "@/components/SensorMonitoring";
import ChatbotWidget from "@/components/ChatbotWidget";

const Hardware = () => {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <Navbar />
      <div className="pt-16">
        <SensorMonitoring />
        <ChatbotWidget />
      </div>
    </main>
  );
};

export default Hardware;
