import { Card } from "@/components/ui/Card";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";

export default function SettingsPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Settings"
        description="Manage your business profile and connected data."
      />
      <Card className="text-sm text-muted">
        Settings content will be implemented in a later phase.
      </Card>
    </PageContainer>
  );
}
