import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, IndianRupee, Calendar, ArrowRight, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

interface Subsidy {
  id: string;
  title: string;
  title_hi: string;
  amount: string;
  description: string;
  eligibility: string;
  deadline: string;
  status: string;
}

const SubsidyInfo = () => {
  const [subsidies, setSubsidies] = useState<Subsidy[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchSubsidies = async () => {
      try {
        const { data, error } = await supabase
          .from('subsidies')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;
        setSubsidies(data || []);
      } catch (error) {
        console.error('Error fetching subsidies:', error);
        toast({
          title: "Error",
          description: "Failed to load subsidy information",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSubsidies();
  }, [toast]);

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

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {subsidies.map((subsidy) => (
            <Card key={subsidy.id} className="shadow-soft hover:shadow-strong transition-all duration-300 hover:-translate-y-1">
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
                <CardDescription className="text-sm">{subsidy.title_hi}</CardDescription>
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
        )}

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