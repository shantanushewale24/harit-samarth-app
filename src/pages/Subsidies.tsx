import Navbar from "@/components/Navbar";
import SubsidyInfo from "@/components/SubsidyInfo";
import ChatbotWidget from "@/components/ChatbotWidget";

const Subsidies = () => {
  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="pt-16">
        <SubsidyInfo />
        <ChatbotWidget />
      </div>
    </main>
  );
};

export default Subsidies;
