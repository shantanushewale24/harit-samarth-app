-- Create subsidies table
CREATE TABLE public.subsidies (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  title_hi TEXT NOT NULL,
  amount TEXT NOT NULL,
  description TEXT NOT NULL,
  eligibility TEXT NOT NULL,
  deadline TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.subsidies ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access (subsidies are public information)
CREATE POLICY "Subsidies are viewable by everyone" 
ON public.subsidies 
FOR SELECT 
USING (true);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER update_subsidies_updated_at
BEFORE UPDATE ON public.subsidies
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Insert initial subsidy data
INSERT INTO public.subsidies (title, title_hi, amount, description, eligibility, deadline, status) VALUES
  ('PM-KISAN Scheme', 'पीएम-किसान योजना', '₹6,000/year', 'Direct income support to all farmer families', 'All landholding farmers', 'Ongoing', 'Active'),
  ('Soil Health Card', 'मृदा स्वास्थ्य कार्ड', 'Free', 'Get soil testing and recommendations', 'All farmers', 'Apply anytime', 'Active'),
  ('Drip Irrigation Subsidy', 'ड्रिप सिंचाई अनुदान', 'Up to 55%', 'Financial support for micro-irrigation', 'Small & marginal farmers', 'March 2024', 'Limited'),
  ('Crop Insurance', 'फसल बीमा योजना', '2% premium', 'Protection against crop loss', 'All farmers', 'Season-wise', 'Active');