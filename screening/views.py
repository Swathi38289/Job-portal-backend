from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .jd_parser import parse_job_description
from .ranking import rank_candidates
from .resume_parser import parse_resume


class ScreenResumesAPIView(APIView):
	parser_classes = (MultiPartParser, FormParser, JSONParser)

	def post(self, request, format=None):
		job_description = request.data.get("job_description")
		job_description_file = request.FILES.get("job_description_file")
		resumes = request.FILES.getlist("resumes")
		use_semantic = str(request.data.get("use_semantic", "false")).lower() in {
			"1",
			"true",
			"yes",
			"on",
		}

		if not job_description and not job_description_file:
			return Response(
				{"detail": "Provide job_description or job_description_file."},
				status=status.HTTP_400_BAD_REQUEST,
			)
		if not resumes:
			return Response(
				{"detail": "Upload at least one resume in the resumes field."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			description = parse_job_description(
				job_description_file or job_description
			)
			candidates = [
				{"filename": resume.name, "resume_text": parse_resume(resume)}
				for resume in resumes
			]
			ranked = rank_candidates(
				candidates,
				description,
				use_semantic=use_semantic,
			)
		except (ValueError, UnicodeDecodeError) as error:
			return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)

		return Response(
			{
				"results": [
					{
						"rank": result["rank"],
						"filename": result["candidate"]["filename"],
						"score": result["score"],
					}
					for result in ranked
				]
			},
			status=status.HTTP_200_OK,
		)
from django.shortcuts import render

# Create your views here.


def screening_home(request):
	return render(request, "screening/index.html")
