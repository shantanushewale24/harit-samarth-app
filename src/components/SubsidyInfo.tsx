import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, IndianRupee, Calendar, ArrowRight } from "lucide-react";

const SubsidyInfo = () => {
  const subsidies = [
    {
      title: "PM-KISAN Scheme",
      titleHi: "पीएम-किसान योजना",
      amount: "₹6,000/year",
      description: "Direct income support to all farmer families",
      eligibility: "All landholding farmers",
      deadline: "Ongoing",
      status: "Active"
    },
    {
      title: "Soil Health Card",
      titleHi: "मृदा स्वास्थ्य कार्ड",
      amount: "Free",
      description: "Get soil testing and recommendations",
      eligibility: "All farmers",
      deadline: "Apply anytime",
      status: "Active"
    },
    {
      title: "Drip Irrigation Subsidy",
      titleHi: "ड्रिप सिंचाई अनुदान",
      amount: "Up to 55%",
      description: "Financial support for micro-irrigation",
      eligibility: "Small & marginal farmers",
      deadline: "March 2024",
      status: "Limited"
    },
    {
      title: "Crop Insurance",
      titleHi: "फसल बीमा योजना",
      amount: "2% premium",
      description: "Protection against crop loss",
      eligibility: "All farmers",
      deadline: "Season-wise",
      status: "Active"
    }
  ];

  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            Government Subsidies
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            सरकारी योजनाएं - Financial support and schemes available for farmers
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {subsidies.map((subsidy, index) => (
            <Card key={index} className="shadow-soft hover:shadow-strong transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <FileText className="h-8 w-8 text-primary" />
                  <Badge 
                    variant={subsidy.status === "Active" ? "default" : "secondary"}
                    className={subsidy.status === "Active" ? "bg-field" : ""}
                  >
                    {subsidy.status}
                  </Badge>
                </div>
                <CardTitle className="text-lg line-clamp-2">{subsidy.title}</CardTitle>
                <CardDescription className="text-sm">{subsidy.titleHi}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-harvest">
                    <IndianRupee className="h-5 w-5" />
                    <span className="text-xl font-bold">{subsidy.amount}</span>
                  </div>

                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {subsidy.description}
                  </p>

                  <div className="space-y-2 text-sm">
                    <div>
                      <p className="text-muted-foreground">Eligibility:</p>
                      <p className="font-medium text-foreground">{subsidy.eligibility}</p>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar className="h-4 w-4" />
                      <span>{subsidy.deadline}</span>
                    </div>
                  </div>

                  <Button className="w-full" variant="outline">
                    Apply Now
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center mt-12">
          <Button size="lg" variant="default">
            View All Schemes
          </Button>
        </div>
      </div>
    </section>
  );
};

export default SubsidyInfo;