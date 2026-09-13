import { Card } from "@/components/ui/Card";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";

export default function DashboardPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Dashboard"
        description="Here's what needs your attention today."
      />
      <Card className="text-sm text-muted">
        Dashboard content will be implemented in a later phase.
      </Card>
    </PageContainer>
  );
}
