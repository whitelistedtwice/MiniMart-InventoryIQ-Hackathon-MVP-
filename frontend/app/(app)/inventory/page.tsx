import { Card } from "@/components/ui/Card";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";

export default function InventoryPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Inventory"
        description="Manage your products and stock levels."
      />
      <Card className="text-sm text-muted">
        Inventory content will be implemented in a later phase.
      </Card>
    </PageContainer>
  );
}
