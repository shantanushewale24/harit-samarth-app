import Navbar from "@/components/Navbar";
import CropRecommendation from "@/components/CropRecommendation";
import ChatbotWidget from "@/components/ChatbotWidget";

const Crops = () => {
  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="pt-16">
        <CropRecommendation />
        <ChatbotWidget />
      </div>
    </main>
  );
};

export default Crops;
