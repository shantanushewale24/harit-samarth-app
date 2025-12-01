import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageSquare, Send, Languages } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const ChatbotWidget = () => {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ? (Hello! How can I help you?)" }
  ]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("hi");

  const handleSend = () => {
    if (!input.trim()) return;
    
    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: language === "hi" 
          ? "मैं आपके सवाल को समझ गया हूँ। मैं आपको सही जानकारी देने की कोशिश कर रहा हूँ।"
          : language === "mr"
          ? "मी तुमचा प्रश्न समजला आहे. मी तुम्हाला योग्य माहिती देण्याचा प्रयत्न करत आहे।"
          : "I understand your question. I'm working on providing you the right information."
      }]);
    }, 1000);
  };

  return (
    <section className="py-16 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            AI Farming Assistant
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            कृषि सहायक - Ask questions in Hindi, Marathi, or English
          </p>
        </div>

        <Card className="max-w-3xl mx-auto shadow-strong">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-6 w-6 text-primary" />
                Chat with Expert
              </CardTitle>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger className="w-[140px]">
                  <Languages className="h-4 w-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hi">हिंदी</SelectItem>
                  <SelectItem value="mr">मराठी</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="h-[400px] overflow-y-auto p-4 bg-secondary/20 rounded-lg space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-card text-card-foreground shadow-soft"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-2">
                <Input
                  placeholder={
                    language === "hi"
                      ? "अपना सवाल यहाँ लिखें..."
                      : language === "mr"
                      ? "तुमचा प्रश्न येथे लिहा..."
                      : "Type your question here..."
                  }
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSend()}
                  className="flex-1"
                />
                <Button onClick={handleSend} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput(language === "hi" ? "मेरी फसल के लिए कौन सा खाद अच्छा है?" : "Which fertilizer is good for my crop?")}
                >
                  {language === "hi" ? "खाद सुझाव" : language === "mr" ? "खत सूचना" : "Fertilizer Tips"}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput(language === "hi" ? "सब्सिडी कैसे मिलेगी?" : "How to get subsidies?")}
                >
                  {language === "hi" ? "सब्सिडी जानकारी" : language === "mr" ? "अनुदान माहिती" : "Subsidy Info"}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput(language === "hi" ? "मौसम की जानकारी" : "Weather information")}
                >
                  {language === "hi" ? "मौसम" : language === "mr" ? "हवामान" : "Weather"}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default ChatbotWidget;