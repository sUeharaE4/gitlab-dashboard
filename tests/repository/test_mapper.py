import pytest
from gitlab.client import Gitlab
from gitlab.v4.objects import GroupManager
from gitlab.v4.objects.groups import Group

from common.errors import ResourceNotFoundError
from repository.mapper import GitlabClient


class TestGitlabClient:
    @pytest.fixture
    def init_client(self, mocker):
        self.client = self.make_dummy_client(mocker)

    @pytest.fixture
    def init_client_no_group(self, mocker):
        self.client = self.make_dummy_client(mocker, False)

    def test_no_group(self, mocker):
        """Test for no group found in the group_id."""
        mock_gl = mocker.Mock(spec=Gitlab)
        mock_goup_manager = mocker.Mock(spec=GroupManager)
        mock_gl.groups = mock_goup_manager
        mocker.patch("gitlab.client.Gitlab", mock_gl)
        mocker.patch("gitlab.v4.objects.GroupManager.get", return_value=None)
        with pytest.raises(ResourceNotFoundError):
            GitlabClient(1)

    @staticmethod
    def make_dummy_client(mocker, has_group: bool = True):
        mock_gl = mocker.Mock(spec=Gitlab)
        mock_group = mocker.Mock(spec=Group)
        mock_goup_manager = mocker.Mock(spec=GroupManager)
        mock_gl.groups = mock_goup_manager
        mock_client = mocker.Mock(spec=GitlabClient)
        mock_client.id = 1
        mock_client.gl = mock_gl
        if has_group:
            mocker.patch("gitlab.v4.objects.GroupManager.get", mock_group)
            mock_client.group = mock_group
        else:
            mocker.patch("gitlab.v4.objects.GroupManager.get", None)
            mock_client.group = None
        return mock_client
