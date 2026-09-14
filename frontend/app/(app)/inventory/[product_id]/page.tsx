import { ProductDetail } from "@/components/inventory/ProductDetail";

/*
  The key forces a full remount when the product changes, so no stock,
  recommendation, chart, or AI state from a previous product can leak into
  the next one.
*/
export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ product_id: string }>;
}) {
  const { product_id } = await params;
  return <ProductDetail key={product_id} productId={product_id} />;
}
