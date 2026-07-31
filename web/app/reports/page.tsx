"use client";

import { useQuery } from "@tanstack/react-query";
import { reportsAPI } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/utils";

export default function ReportsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: () => reportsAPI.list(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Reports</h2>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading reports...</div>
      ) : !data?.items?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No reports generated yet. Reports are created automatically by the Reporter agent.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.items.map((report: any) => (
            <Card key={report.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="p-4">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-sm">{report.title}</CardTitle>
                  <Badge variant="outline" className="capitalize">
                    {report.doc_type?.replace(/_/g, " ")}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <p className="text-xs text-gray-500 line-clamp-3">{report.content?.slice(0, 200)}</p>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xs text-gray-400">{formatDateTime(report.created_at)}</span>
                  {report.file_url && (
                    <a
                      href={report.file_url}
                      className="text-xs text-mantis-600 hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Download
                    </a>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
