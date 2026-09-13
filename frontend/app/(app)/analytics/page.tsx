import { Card } from "@/components/ui/Card";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";

export default function AnalyticsPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Analytics"
        description="Understand your sales, inventory and trends."
      />
      <Card className="text-sm text-muted">
        Analytics content will be implemented in a later phase.
      </Card>
    </PageContainer>
  );
}
